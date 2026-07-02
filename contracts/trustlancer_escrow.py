# contracts/trustlancer_escrow.py
from genlayer import IntelligentContract, address, bigint, current_block, llm_node

class TrustLancerEscrow(IntelligentContract):
    def __init__(self):
        # এসক্রোর বিভিন্ন স্টেট (Status)
        self.STATUS_INITIALIZED = 0
        self.STATUS_FUNDED = 1
        self.STATUS_DISPUTED = 2
        self.STATUS_RESOLVED_TO_FREELANCER = 3
        self.STATUS_REFUNDED_TO_CLIENT = 4

        # গ্লোবাল ভেরিয়েবলস
        self.client: address = None
        self.freelancer: address = None
        self.amount: bigint = bigint(0)
        self.requirements: str = ""
        self.delivery_link: str = ""
        self.status: int = self.STATUS_INITIALIZED
        self.dispute_reason: str = ""
        self.ai_judgment: str = ""

    def create_job(self, freelancer_address: address, job_requirements: str):
        """ক্লায়েন্ট নতুন জব ক্রিয়েট করবে এবং রিকোয়ারমেন্ট সেট করবে"""
        assert self.status == self.STATUS_INITIALIZED, "Job already initialized or active!"
        
        self.client = current_block().tx_sender
        self.freelancer = freelancer_address
        self.requirements = job_requirements
        self.status = self.STATUS_FUNDED
        
        # জেনলেয়ারে ফান্ড ডিপোজিট ট্র্যাকিং (ভ্যালু ট্রান্সফার এগ্রিমেন্ট)
        self.amount = current_block().tx_value
        assert self.amount > 0, "You must deposit some funds to secure the escrow!"

    def submit_work(self, submission_link: str):
        """ফ্রিল্যান্সার তার কাজের গিটহাব বা লাইভ লিংক সাবমিট করবে"""
        assert self.status == self.STATUS_FUNDED, "Escrow is not in funded state."
        assert current_block().tx_sender == self.freelancer, "Only the assigned freelancer can submit work!"
        assert len(submission_link) > 0, "Submission link cannot be empty!"
        
        self.delivery_link = submission_link

    def release_payment(self):
        """সব ঠিক থাকলে ক্লায়েন্ট ম্যানুয়ালি পেমেন্ট রিলিজ করে দিতে পারে"""
        assert self.status == self.STATUS_FUNDED or self.status == self.STATUS_DISPUTED, "Invalid escrow state."
        assert current_block().tx_sender == self.client, "Only the client can manually release payment!"
        
        self.status = self.STATUS_RESOLVED_TO_FREELANCER
        # ফ্রিল্যান্সারের ওয়ালেটে ফান্ড ট্রান্সফার
        self.transfer(self.freelancer, self.amount)

    def trigger_ai_dispute(self, client_complaint: str):
        """বায়ার বা সেলারের মধ্যে ঝামেলা হলে এই ফাংশন AI জাজমেন্ট কল করবে"""
        assert self.status == self.STATUS_FUNDED, "Dispute can only be triggered for funded jobs."
        assert current_block().tx_sender == self.client or current_block().tx_sender == self.freelancer, "Unauthorized party!"
        assert len(self.delivery_link) > 0, "Freelancer hasn't submitted any work yet to dispute!"
        
        self.status = self.STATUS_DISPUTED
        self.dispute_reason = client_complaint

        # 🤖 জেনলেয়ারের আসল ম্যাজিক: LLM নোড দিয়ে গিটহাব/ওয়েবসাইট ও রিকোয়ারমেন্ট স্ক্র্যাপ করে জাজমেন্ট নেওয়া
        prompt = f"""
        You are an elite, unbiased Decentralized AI Freelance Arbitrator for GenLayer.
        
        Review the following case carefully:
        - Job Requirements provided by Client: {self.requirements}
        - Freelancer's Work Delivery Link: {self.delivery_link}
        - Client's Complaint/Dispute Reason: {client_complaint}
        
        Task: 
        Analyze if the Freelancer has genuinely attempted and completed the core features requested in the requirements based on their delivery link. 
        Provide a detailed explanation of your analysis.
        At the absolute end of your response, you MUST output exactly one of these two phrases:
        "VERDICT: RELEASE_FUNDS" (if the freelancer did the work correctly) or 
        "VERDICT: REFUND_CLIENT" (if the freelancer completely failed or scammed).
        """

        # জেনলেয়ারের বিল্ট-ইন LLM কলিং মেথড (কনসেনসাস নোড এক্সিকিউশন)
        response = llm_node().call(prompt)
        self.ai_judgment = response

        # রায় অনুযায়ী অটোমেটিক অন-চেইন ফান্ড রিলিজ বা রিফান্ড
        if "VERDICT: RELEASE_FUNDS" in response:
            self.status = self.STATUS_RESOLVED_TO_FREELANCER
            self.transfer(self.freelancer, self.amount)
        elif "VERDICT: REFUND_CLIENT" in response:
            self.status = self.STATUS_REFUNDED_TO_CLIENT
            self.transfer(self.client, self.amount)

    def get_escrow_details(self) -> dict:
        """ড্যাশবোর্ডে বা ফ্রন্টএন্ডে ডেটা দেখানোর জন্য ভিউ ফাংশন"""
        return {
            "client": self.client,
            "freelancer": self.freelancer,
            "amount": str(self.amount),
            "requirements": self.requirements,
            "delivery_link": self.delivery_link,
            "status": self.status,
            "dispute_reason": self.dispute_reason,
            "ai_judgment": self.ai_judgment
        }
