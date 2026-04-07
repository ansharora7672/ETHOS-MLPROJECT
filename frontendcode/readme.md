
# 🌌 Project E.T.H.O.S.
### Extraterrestrial Target Habitability Observation System

[cite_start]Project E.T.H.O.S. is an automated AI pipeline designed to transform raw space data into a ranked list of potentially habitable worlds[cite: 53, 56]. [cite_start]Developed for the PROG74000 course, this system addresses the "noise" bottleneck in astronomical data by using machine learning to distinguish real planets from telescope glitches[cite: 2, 4, 7].

---

## 🎯 Project Motivation
[cite_start]Space telescopes like Kepler capture thousands of signals, but many are "False Positives" caused by binary stars, sunspots, or instrument errors[cite: 5, 32, 33]. [cite_start]Manually verifying these is an impossible, time-consuming task for astrobiologists[cite: 34, 44].

[cite_start]**The Goal:** Create an automatic system that quickly filters out fake signals and immediately evaluates real planets for their potential to support life[cite: 46, 47].

---

## 🛠️ Tech Stack
* [cite_start]**Language:** Python 3.13 [cite: 58]
* [cite_start]**Frontend:** Streamlit (Interactive Web UI) [cite: 63]
* [cite_start]**Machine Learning:** Scikit-Learn (Random Forest) and PyTorch (Multi-Layer Perceptron) [cite: 60, 61, 75, 76]
* [cite_start]**Cloud & Tools:** VS Code, Git, Google Colab, and AWS EC2 [cite: 59, 62, 64]

---

## 🧬 The AI Pipeline
[cite_start]The system operates as a two-stage machine learning pipeline[cite: 17]:

1.  **Phase 1: Exoplanet Discovery Classifier**
    * [cite_start]**Task:** Binary Classification[cite: 69, 81].
    * [cite_start]**Input:** Raw Kepler Cumulative Objects of Interest (KOI) data from the NASA Exoplanet Archive[cite: 68].
    * [cite_start]**Output:** Identifies if a signal is "CONFIRMED" (an exoplanet) or a "FALSE POSITIVE"[cite: 69].

2.  **Phase 2: Habitability Assessor**
    * [cite_start]**Task:** Regression[cite: 94].
    * [cite_start]**Input:** Physical traits of confirmed planets, such as radius and surface temperature[cite: 14, 85].
    * [cite_start]**Output:** Predicts an **Earth Similarity Index (ESI)** score between 0.00 and 1.00[cite: 22, 83].

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/ArshChauhan1101/E.T.H.O.S.git](https://github.com/ArshChauhan1101/E.T.H.O.S.git)
cd E.T.H.O.S.
```

### 2. Set Up Virtual Environment(Optional)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```
### 3. Install Dependencies
```bash
pip install streamlit pandas numpy scikit-learn torch
```

### 4. Launch the App
```bash
streamlit run main.py
```

## Group 9 Team Members
Arsh Chauhan 
Girish Bhuteja 
Tanishk Sharma 
Ansh Arora 