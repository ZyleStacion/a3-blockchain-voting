# DAO-based governance for a transparent donation app

## Core Features
1. Voting -> Blockchain
	- Users sign each vote
2. Ticket purchasing w/ quadratic voting
3. Login + Logout
4. Registration
	- Each user has a key-pair
5. Transactions -> Blockchain
	- Dummy data
	- Users sign each transaction
6. Voting results
	- See who voted (alias - ZKP)
7. Profile (opt.) -> Database

## Pages
Static Contents
	1. Landing
		1. There is currently XX amount of money in the pot...
		2. Technical info
	2. Profile
		1. Dashboard
		2. Login
		3. Signup
	3. Voting form (select from like 4 or 5 charities)

Dynamic Contents:
	1. Post-voting live result counter (opt)
	2. Admin dashboard
	3. Blockchain view - can be in the console

## Created by
- Kim ‘Jay’ JongOh s3726103
- Thinh Nguyen Huynh Trieu s3977756 
- Zyle Estacion s4064846 

## Installation and Setup
Please install the following dependencies:

### Backend:
```bash
# TODO: Install dependencies
cd backend
uvicorn main
127.0.01:8080
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```
- @chakra-ui/react
- @emotion/react
- @emotion/styled
- framer-motion
- @vitejs/plugin-react