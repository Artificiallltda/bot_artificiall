import threading
import queue
import time
import asyncio
import PySimpleGUI as sg

# Try to import backend AutomationApp
try:
	from backend.main import AutomationApp
	backend_app = AutomationApp()
except Exception as e:
	backend_app = None
	backend_import_error = str(e)

# Fila local de jobs
job_queue = queue.Queue()

def process_job(job):
	# TODO: integrar com o backend. Exemplo:
	if backend_app is None:
		return {"status": "error", "result": f"Backend not available: {backend_import_error}"}

	try:
		# run the async processing synchronously per job
		res = asyncio.run(backend_app.process_download_and_upload(job))
		return {"status": "done", "result": res}
	except Exception as e:
		return {"status": "error", "result": str(e)}

def worker_loop(window):
	while True:
		job = job_queue.get()
		if job is None:
			break
		window.write_event_value('-JOB_STARTED-', job)
		try:
			res = process_job(job)
			window.write_event_value('-JOB_DONE-', (job, res))
		except Exception as e:
			window.write_event_value('-JOB_ERROR-', (job, str(e)))
		job_queue.task_done()

layout = [
	[sg.Text("Cole links (uma por linha):")],
	[sg.Multiline(key='-LINKS-', size=(60,6))],
	[sg.Button("Enviar"), sg.Button("Iniciar Worker"), sg.Button("Parar Worker"), sg.Button("Sair")],
	[sg.Text("Fila de Jobs:")],
	[sg.Listbox(values=[], size=(80,8), key='-JOB_LIST-')],
	[sg.Text("Logs:")],
	[sg.Multiline(size=(80,10), key='-LOG-', disabled=True)]
]

window = sg.Window("Automation Bot — GUI", layout, finalize=True)

worker_thread = None

while True:
	event, values = window.read()
	if event in (sg.WIN_CLOSED, "Sair"):
		if worker_thread and worker_thread.is_alive():
			job_queue.put(None)
			worker_thread.join()
		break

	if event == "Enviar":
		links = values['-LINKS-'].strip().splitlines()
		for l in links:
			if not l.strip():
				continue
			job_queue.put(l.strip())
		current = list(window['-JOB_LIST-'].get_list_values())
		current += [f"Queued: {l.strip()}" for l in links if l.strip()]
		window['-JOB_LIST-'].update(current)
		window['-LOG-'].update("Links enfileirados\n", append=True)

	if event == "Iniciar Worker":
		if not worker_thread or not worker_thread.is_alive():
			worker_thread = threading.Thread(target=worker_loop, args=(window,), daemon=True)
			worker_thread.start()
			window['-LOG-'].update("Worker iniciado\n", append=True)

	if event == "Parar Worker":
		if worker_thread and worker_thread.is_alive():
			job_queue.put(None)
			worker_thread.join(timeout=5)
			window['-LOG-'].update("Worker parado\n", append=True)

	if event == '-JOB_STARTED-':
		job = values[event]
		window['-LOG-'].update(f"Processando: {job}\n", append=True)

	if event == '-JOB_DONE-':
		job, res = values[event]
		window['-LOG-'].update(f"Concluído: {job} -> {res}\n", append=True)

	if event == '-JOB_ERROR-':
		job, err = values[event]
		window['-LOG-'].update(f"Erro: {job} -> {err}\n", append=True)

window.close()
