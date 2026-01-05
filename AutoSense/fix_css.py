
import os

target_file = r"e:\Fraudnet\FraudNET\FraudNET\AutoSense\frontend\style.css"
new_css = """
/* AI BRAIN UI */
.ai-glow-orb {
    position: absolute;
    width: 60px;
    height: 60px;
    background: radial-gradient(circle, var(--accent), transparent 70%);
    border-radius: 50%;
    filter: blur(20px);
    opacity: 0.6;
    animation: pulseGlow 4s infinite alternate;
    left: 20px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 1;
}

@keyframes pulseGlow {
    0% { opacity: 0.4; transform: translateY(-50%) scale(0.8); }
    100% { opacity: 0.8; transform: translateY(-50%) scale(1.2); }
}

.ai-chat-bubble {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--glass-border);
    padding: 15px 20px;
    border-radius: 0 16px 16px 16px;
    margin-top: 10px;
    font-size: 0.95rem;
    line-height: 1.5;
    color: rgba(255, 255, 255, 0.9);
    position: relative;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    display: flex;
    align-items: center;
    min-height: 50px;
}

.ai-chat-bubble::before {
    content: '';
    position: absolute;
    top: 0;
    left: -10px;
    border-top: 10px solid rgba(255, 255, 255, 0.05);
    border-left: 10px solid transparent;
}

.badge {
    font-size: 0.7em;
    padding: 4px 8px;
    border-radius: 4px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid var(--glass-border);
    color: var(--accent);
    letter-spacing: 1px;
    font-weight: bold;
}
"""

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Locate the retry-btn closing brace
# We know it ends around there.
if ".retry-btn" in content:
    # Split by .retry-btn to confirm location
    parts = content.split(".retry-btn")
    # Taking the last part
    last_part = parts[-1]
    # Find the closing brace '}' in last_part
    brace_index = last_part.find('}')
    
    if brace_index != -1:
        # Reconstruct content up to that brace
        # parts[:-1] joins everything before the last occurrence of .retry-btn
        # plus ".retry-btn"
        # plus the start of last_part up to brace_index + 1
        clean_content = ".retry-btn".join(parts[:-1]) + ".retry-btn" + last_part[:brace_index+1]
        
        # Append new CSS
        final_content = clean_content + "\n" + new_css
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(final_content)
        print("SUCCESS: Fixed CSS file.")
    else:
        print("ERROR: Could not find closing brace for .retry-btn")
else:
    print("ERROR: Could not find .retry-btn class")
