# Future Enhancements for the Real-time Event Announcement System

This document outlines potential improvements and new features that can be added to the current system. These enhancements aim to increase scalability, robustness, security, and user experience.

---

## 1. Data Management & Scalability

* **Replace `events.json` with DynamoDB:**
    * **Why:** The current approach of modifying a single `events.json` file in S3 is prone to race conditions, limits scalability, and can be inefficient for frequent updates. DynamoDB offers a highly scalable, fully managed NoSQL database solution.
    
* **Event Archiving/Cleanup:**
    * Implement a mechanism to automatically archive or delete old events from DynamoDB or S3 (if still using `events.json`) after a certain period.

## 2. Real-time Website Updates

* **Implement WebSockets for Instant Updates:**
    * **Why:** Currently, the website relies on calling `loadEvents()` after a new event submission. For truly instant updates across all active user browsers without manual refreshes, WebSockets are ideal.
    
## 3. Security & Access Control

* **Fine-Grained IAM Permissions:**
    * **Why:** The current IAM roles use `*FullAccess` policies. For production, apply the principle of least privilege.
   
* **User Authentication for Event Submission:**
    * **Why:** Currently, anyone with the API Gateway endpoint can submit events. Restrict this to authorized users.
    
* **Web Application Firewall (WAF):**
    * **Why:** Protect API Gateway endpoints from common web exploits (e.g., SQL injection, cross-site scripting).
    



## 4. Monitoring & Observability

* **Custom CloudWatch Alarms:**
    * **Why:** Proactive notification of system issues.
   


## 5. Custom Domain & CDN

* **Custom Domain Name:**
    * **Why:** A more professional and user-friendly URL for your website and API (e.g., `events.yourcompany.com` instead of S3/API Gateway URLs).
    

---

These enhancements can be tackled incrementally, allowing us to gradually build out a more robust and feature-rich real-time event announcement system.
