# 🎙️ Judge Q&A Cheat Sheet - ElectroSphere 2K26

**Use these answers to score full marks in the Q&A section.**

---

### **Q1: What makes your project different from other PC Cleaners (like CCleaner)?**
**Answer:** "Most cleaners are *reactive*—they wait for you to press a button. AutoSense is *proactive* and *intelligent*. We use an **Isolation Forest specific Machine Learning model** to analyze system behavior over time. It doesn't just look at 'high CPU' usage; it looks for *abnormal* usage patterns specific to THIS computer, protecting the user before the system even freezes."

---

### **Q2: Why did you choose Python/FastAPI for the backend?**
**Answer:** "We needed a balance between raw system access and AI capabilities. Python helps us access the Windows Registry and System Kernels easily (via `psutil` and `winreg`) while giving us immediate access to powerful ML libraries like `scikit-learn`. FastAPI provides the speed of NodeJS with the power of Python, handling async monitoring tasks without slowing down the user's PC."

---

### **Q3: How does your AI actually work? Is it just if-statements?**
**Answer:** "We use a Hybrid approach.
1. **Immediate Layer (Heuristic):** Yes, we use threshold checks (like `if RAM > 90%`) for critical emergencies because they are instant.
2. **Predictive Layer (ML):** We use the `sklearn.ensemble.IsolationForest` algorithm. It trains on the user's historical CPU/RAM data to define 'normal' behavior. If a process starts behaving weirdly (even if it's not at 100% CPU), the model flags it as an anomaly based on its deviation from multiple vectors. This allows us to catch memory leaks *before* they crash the system."

---

### **Q4: What was the biggest challenge you faced?**
**Answer:** "The hardest part was **Performance Overhead**. Building a tool to fix performance shouldn't cause performance issues itself. We solved this by:
1. Optimizing our frontend to use Zero Dependencies (Vanilla JS).
2. Running the AI inference asynchronously in the background only when resources are available.
3. Using efficient data structures to store only the last N monitoring records to prevent memory bloat."

---

### **Q5: How can this be scaled or turned into a real product?**
**Answer:** "We can easily scale this to an **Enterprise Fleet Manager**. By sending the anomaly data to a central cloud server, IT admins could predict which employee laptops are about to crash or need maintenance weeks in advance, saving companies thousands of dollars in lost productivity and hardware repairs."

---
**Key Terms to Drop:**
- "Asynchronous Non-blocking I/O"
- "Unsupervised Learning"
- "Resource Contention"
- "Heuristic vs Stochastic Analysis"
