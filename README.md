# TrustLancer AI: Decentralized Intelligent Freelance Escrow

TrustLancer AI is an original dApp built from scratch on top of GenLayer's network architecture. The platform introduces completely decentralized, bias-free freelance escrow arbitration by replacing human mediators with GenLayer's consensus-driven Intelligent Contracts.

## The Real-World Problem
Traditional freelance escrow systems (like Upwork or Web3 multisigs) rely on centralized support agents or manual human juries to solve disputes when a client claims the work is incomplete. This leads to high fees, delayed payouts, and subjective bias.

## How GenLayer Solves It
By utilizing GenLayer's `IntelligentContract` framework, the contract acts as both the vault and the judge:
1. **Secure Funding:** Clients lock the project budget directly into the contract alongside explicit requirements.
2. **On-Chain AI Arbitration:** If a dispute arises, the contract invokes the internal `llm_node()` engine. 
3. **Automated Scraping & Logic:** The AI nodes read the freelancer's live repository/delivery URL, analyze the actual code structure against the locked raw requirements, and execute an automated, irreversible on-chain transaction (`RELEASE_FUNDS` or `REFUND_CLIENT`).

## Repository Structure
- `/contracts`: Core backend Python script containing the `TrustLancerEscrow` Intelligent Contract logic.
- `/frontend`: Minimalistic UI layout built for user interaction with the Bradbury Testnet.

## Core Contract Methods Implemented
- `create_job(freelancer_address, job_requirements)`: Initializes states and handles secure value deposits.
- `submit_work(submission_link)`: Allows the freelancer to formally attach their work evidence.
- `release_payment()`: Standard direct routing path for successful job completion.
- `trigger_ai_dispute(client_complaint)`: Triggers the LLM consensus state machine to parse the verdict.

## Local Configuration & Deployment Note
The intelligent contract is written natively using the `genlayer` Python SDK. It can be built and deployed via the standard GenLayer CLI tooling or connected directly to the Bradbury testnet environment using browser wallet extensions.
