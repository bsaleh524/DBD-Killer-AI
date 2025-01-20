•	Eyes
o	Object Detections (survivors, generators, etc)
o	OCR
o	Input:
	Screen capture
o	Output:
	Object detections
	Bottom OCR (interactions)
	Top Right OCR (rewards)
•	Brain (AI, send to controls)
o	Reward function
o	Decision making
o	commands arms and legs signals to perform actions
o	Input:
	Object Detections
	Top Right OCR (rewards)
	Bottom OCR (nteractions)
	TBD
o	Output:
	Legs commands
	Arms commands
	Neck commands?
•	Neck
o	Turn head to face detections (pyautogui)
o	Input:
	Object Detections
	Commands from Brain?
•	Arms (Controls)
o	Mouse 1 and 2
o	Input:
	Commands from Brain
•	Legs (controls)
o	Movement(pyautogui)
o	Input:
	Commands from Brain


* threading: concurrent tasks. io bound. Waiting for input and output operations.
* multiprocessing: Parallel