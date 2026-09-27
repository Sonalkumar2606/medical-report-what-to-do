import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st

# Load environment variables from root .env or test/.env
root_env_path = Path(__file__).resolve().parent / ".env"
test_env_path = Path(__file__).resolve().parent / "test" / ".env"

if root_env_path.exists():
    load_dotenv(dotenv_path=root_env_path)
elif test_env_path.exists():
    load_dotenv(dotenv_path=test_env_path)
else:
    load_dotenv()

#DEFAULT_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEFAULT_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
#DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
DEFAULT_MODEL = st.secrets.get("OPENROUTER_MODEL", "openai/gpt-oss-120b")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# 1. Page Configuration & Title
st.set_page_config(page_title="CBC Medical Report Analyzer", page_icon="🩺", layout="centered")

st.title("🩺 Medical Report Analyzer")
st.write("A comprehensive web application with **Rule-Based Clinical Guidance** and **Advanced AI Interpretation** for Complete Blood Count (CBC) test parameters.")

# 2. Patient Details & Settings in Sidebar
st.sidebar.header("📋 Patient Details")
patient_name = st.sidebar.text_input("Full Name", value="Alex Smith")
patient_age = st.sidebar.number_input("Age (years)", min_value=1, max_value=120, value=28, step=1)
patient_gender = st.sidebar.selectbox("Gender", options=["Male", "Female"])

# AI Model Configuration (loaded from environment)
ai_model = DEFAULT_MODEL
ai_api_key = DEFAULT_API_KEY

# 3. Manual Parameter Inputs on Main Page with 'Not in report / Don't know'
st.subheader("🔬 Enter Blood Test Parameters")
st.caption("Agar report me koi parameter nahi hai ya aapko nahi pata, to uske upar **'Don't know / Not in report'** tick kar dein.")

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 🩸 Hemoglobin")
    hb_unk = st.checkbox("Don't know / Not in report", key="hb_unk")
    hb = st.number_input("Hemoglobin (g/dL)", min_value=0.0, max_value=30.0, value=14.0, step=0.1, disabled=hb_unk)
    st.caption("Normal: 13.5 - 17.5 g/dL (Male) | 12.0 - 15.5 g/dL (Female)")
    st.divider()

    st.markdown("##### 🔴 RBC Count")
    rbc_unk = st.checkbox("Don't know / Not in report", key="rbc_unk")
    rbc = st.number_input("RBC Count (million/mcL)", min_value=0.0, max_value=15.0, value=4.8, step=0.1, disabled=rbc_unk)
    st.caption("Normal: 4.5 - 5.9 (Male) | 4.0 - 5.2 million/mcL (Female)")
    st.divider()

    st.markdown("##### ⚪ WBC Count")
    wbc_unk = st.checkbox("Don't know / Not in report", key="wbc_unk")
    wbc = st.number_input("WBC Count (/mcL)", min_value=0, max_value=100000, value=7500, step=100, disabled=wbc_unk)
    st.caption("Normal: 4,000 - 11,000 /mcL")
    st.divider()

    st.markdown("##### 🛡️ Neutrophils")
    neutrophils_unk = st.checkbox("Don't know / Not in report", key="neutrophils_unk")
    neutrophils = st.number_input("Neutrophils (%)", min_value=0.0, max_value=100.0, value=60.0, step=0.5, disabled=neutrophils_unk)
    st.caption("Normal: 40 - 70%")

with col2:
    st.markdown("##### 🔬 Lymphocytes")
    lymphocytes_unk = st.checkbox("Don't know / Not in report", key="lymphocytes_unk")
    lymphocytes = st.number_input("Lymphocytes (%)", min_value=0.0, max_value=100.0, value=30.0, step=0.5, disabled=lymphocytes_unk)
    st.caption("Normal: 20 - 40%")
    st.divider()

    st.markdown("##### 🩹 Platelet Count")
    platelets_unk = st.checkbox("Don't know / Not in report", key="platelets_unk")
    platelets = st.number_input("Platelet Count (/mcL)", min_value=0, max_value=1500000, value=250000, step=5000, disabled=platelets_unk)
    st.caption("Normal: 150,000 - 450,000 /mcL")
    st.divider()

    st.markdown("##### 🧪 HCT / Hematocrit")
    hct_unk = st.checkbox("Don't know / Not in report", key="hct_unk")
    hct = st.number_input("HCT / Hematocrit (%)", min_value=0.0, max_value=100.0, value=42.0, step=0.5, disabled=hct_unk)
    st.caption("Normal: 40 - 50% (Male) | 36 - 46% (Female)")
    st.divider()

    st.markdown("##### 📏 MPV (Mean Platelet Volume)")
    mpv_unk = st.checkbox("Don't know / Not in report", key="mpv_unk")
    mpv = st.number_input("MPV - Mean Platelet Volume (fL)", min_value=0.0, max_value=30.0, value=9.5, step=0.1, disabled=mpv_unk)
    st.caption("Normal: 7.5 - 11.5 fL")



# =========================================================
# ADVANCED HEALTH ADVICE DICTIONARY FOR ABNORMAL (LOW/HIGH)
# Har parameter me: do, dont, situations, red_flags, lifestyle
# =========================================================

HEALTH_ADVICE = {

    "Hemoglobin": {
        "Low": {
            "do": [
                "Eat iron-rich foods: spinach, beetroot, pomegranate, lentils, dates, jaggery, red meat (if non-veg).",
                "Take vitamin C (orange, amla, lemon) with iron meals to boost absorption.",
                "Cook in cast-iron utensils to increase iron content.",
                "Take iron supplements only if prescribed by doctor.",
                "Get tested for vitamin B12, folate, and stool occult blood."
            ],
            "dont": [
                "Drink tea/coffee/milk directly with iron-rich meals (blocks absorption).",
                "Ignore heavy menstrual bleeding or black stools.",
                "Self-medicate with high-dose iron without checking ferritin levels."
            ],
            "situations": {
                "Mild (10-12 g/dL)": "Dietary changes + retest after 4-6 weeks.",
                "Moderate (8-10 g/dL)": "Doctor consultation + iron/B12 supplements + investigate cause.",
                "Severe (<8 g/dL)": "Urgent medical attention; may need IV iron or transfusion.",
                "Pregnancy": "Routine iron-folic acid supplementation; monitor closely.",
                "Heavy periods": "Gynecologist consult; check for fibroids/PCOS."
            },
            "red_flags": [
                "Chest pain, breathlessness at rest, palpitations",
                "Black/tarry stools or blood in stool",
                "Severe fatigue, fainting, confusion",
                "Rapid heartbeat with pale skin"
            ],
            "lifestyle": "Adequate sleep, avoid over-exertion, manage stress, treat underlying infections."
        },
        "High": {
            "do": [
                "Stay well-hydrated (3-4 liters water daily).",
                "Donate blood if eligible and advised by doctor.",
                "Avoid iron supplements and vitamin C mega-doses.",
                "Get tested for polycythemia vera, sleep apnea, and liver/kidney issues."
            ],
            "dont": [
                "Smoke or consume alcohol excessively.",
                "Ignore persistent headaches, dizziness, or blurred vision.",
                "Live in high-altitude without acclimatization."
            ],
            "situations": {
                "Mild elevation": "Hydration + repeat test; rule out dehydration.",
                "Moderate elevation": "Hematologist consult; check EPO levels, JAK2 mutation.",
                "Severe elevation": "Risk of clots/stroke; may need phlebotomy or medication.",
                "Smoker": "Quit smoking; carbon monoxide increases RBC.",
                "Sleep apnea": "Treat apnea; CPAP may normalize levels."
            },
            "red_flags": [
                "Sudden chest pain or shortness of breath",
                "Severe headache, vision changes, confusion",
                "Swelling/pain in one leg (DVT sign)",
                "Uncontrolled itching after warm shower"
            ],
            "lifestyle": "Regular aerobic exercise, avoid dehydration, annual blood tests."
        }
    },

    "RBC Count": {
        "Low": {
            "do": [
                "Eat folate & B12 rich foods: eggs, dairy, fortified cereals, green leafy vegetables.",
                "Include protein in every meal (dal, paneer, chicken, fish).",
                "Get B12 injection if deficient (as prescribed).",
                "Check for chronic blood loss (piles, ulcers, menstrual)."
            ],
            "dont": [
                "Skip meals or crash diet.",
                "Over-exercise without rest.",
                "Ignore tingling/numbness in hands/feet (B12 deficiency sign)."
            ],
            "situations": {
                "Nutritional deficiency": "Diet + supplements; retest in 6-8 weeks.",
                "Chronic disease (kidney/liver)": "Treat underlying cause.",
                "Bone marrow issue": "Hematologist + bone marrow biopsy may be needed.",
                "Pregnancy": "Normal dilutional anemia; monitor Hb & RBC."
            },
            "red_flags": [
                "Extreme weakness, breathlessness",
                "Neurological symptoms (memory loss, tingling)",
                "Jaundice or dark urine"
            ],
            "lifestyle": "Balanced diet, moderate exercise, adequate sleep, avoid alcohol."
        },
        "High": {
            "do": [
                "Drink plenty of water (3-4 L/day).",
                "Moderate aerobic exercise (walking, cycling).",
                "Check for sleep apnea, smoking, high altitude, heart/lung disease.",
                "Consider blood donation if medically cleared."
            ],
            "dont": [
                "Smoke or use tobacco.",
                "Ignore persistent headaches, dizziness, or visual disturbances.",
                "Take testosterone or EPO without prescription."
            ],
            "situations": {
                "Dehydration": "Rehydrate and retest.",
                "Sleep apnea": "Sleep study + CPAP.",
                "Polycythemia vera": "Hematologist; may need phlebotomy.",
                "High altitude": "Acclimatize gradually; monitor symptoms."
            },
            "red_flags": [
                "Chest pain, shortness of breath",
                "Severe headache, blurred vision",
                "Leg swelling/pain (clot risk)"
            ],
            "lifestyle": "Hydration, no smoking, regular cardiovascular check-ups."
        }
    },

    "WBC Count": {
        "Low": {
            "do": [
                "Strict personal hygiene; wash hands frequently.",
                "Eat fresh, well-cooked meals; avoid raw/undercooked food.",
                "Get adequate sleep (7-9 hours).",
                "Monitor temperature twice daily; report fever >100.4°F.",
                "Ask doctor about vaccination (flu, pneumococcal)."
            ],
            "dont": [
                "Eat raw street food or unpasteurized dairy.",
                "Visit crowded places during flu season.",
                "Share utensils/towels with sick people.",
                "Ignore recurrent infections."
            ],
            "situations": {
                "Mild (3000-4000/µL)": "Repeat test; monitor for infections.",
                "Moderate (1000-3000/µL)": "Doctor consult; investigate viral/bacterial cause.",
                "Severe (<1000/µL)": "Urgent hematology consult; may need isolation & G-CSF.",
                "Chemotherapy": "Follow oncologist's neutropenic precautions.",
                "Viral infection": "Rest, hydration, retest after recovery."
            },
            "red_flags": [
                "Fever >101°F with chills",
                "Mouth ulcers, sore throat that worsens",
                "Difficulty breathing",
                "Severe fatigue, unexplained bruising"
            ],
            "lifestyle": "Avoid crowds, maintain hygiene, stress management, regular follow-up."
        },
        "High": {
            "do": [
                "Rest adequately; stay hydrated.",
                "Consult doctor to rule out bacterial/viral infection.",
                "Take prescribed antibiotics/antivirals completely.",
                "Repeat CBC after treatment to confirm normalization."
            ],
            "dont": [
                "Self-medicate with leftover antibiotics.",
                "Ignore persistent fever, cough, or pain.",
                "Smoke or consume alcohol during infection."
            ],
            "situations": {
                "Bacterial infection": "Antibiotics as prescribed; retest after 1-2 weeks.",
                "Viral infection": "Supportive care; WBC may normalize in 2-4 weeks.",
                "Leukemia/lymphoma": "Urgent hematologist/oncologist referral.",
                "Stress/inflammation": "Lifestyle changes; retest.",
                "Steroid use": "Review medications with doctor."
            },
            "red_flags": [
                "Fever >102°F lasting >3 days",
                "Unexplained weight loss",
                "Night sweats, bone pain",
                "Easy bruising/bleeding"
            ],
            "lifestyle": "Balanced diet, regular exercise, adequate sleep, avoid smoking."
        }
    },

    "Neutrophils": {
        "Low": {
            "do": [
                "Wash fruits/vegetables thoroughly; peel when possible.",
                "Monitor temperature for sudden fever.",
                "Avoid contact with people having active flu/viral symptoms.",
                "Use hand sanitizer frequently.",
                "Follow neutropenic diet if advised."
            ],
            "dont": [
                "Come in contact with sick people.",
                "Eat raw sprouts, sushi, or unpasteurized products.",
                "Ignore fever even if mild."
            ],
            "situations": {
                "Mild (1000-1500/µL)": "Monitor; repeat test.",
                "Moderate (500-1000/µL)": "Doctor consult; infection precautions.",
                "Severe (<500/µL)": "Urgent care; may need hospitalization.",
                "Post-chemo": "Follow oncologist's protocol.",
                "Drug-induced": "Review medications with doctor."
            },
            "red_flags": [
                "Fever ≥100.4°F",
                "Chills, rapid breathing",
                "Mouth/throat ulcers",
                "Severe weakness"
            ],
            "lifestyle": "Strict hygiene, avoid crowds, adequate rest, nutritious diet."
        },
        "High": {
            "do": [
                "Drink adequate fluids.",
                "Get proper physical rest.",
                "Treat underlying infection/inflammation.",
                "Repeat CBC after treatment."
            ],
            "dont": [
                "Ignore local injury, swelling, or persistent fever.",
                "Self-medicate with steroids.",
                "Smoke or consume alcohol."
            ],
            "situations": {
                "Bacterial infection": "Antibiotics; retest.",
                "Inflammation": "Treat cause; anti-inflammatory diet.",
                "Stress/exercise": "Rest; retest.",
                "Smoking": "Quit smoking.",
                "Myeloproliferative disorder": "Hematologist consult."
            },
            "red_flags": [
                "High fever with chills",
                "Severe pain/swelling",
                "Difficulty breathing",
                "Confusion"
            ],
            "lifestyle": "Hydration, rest, balanced diet, no smoking."
        }
    },

    "Lymphocytes": {
        "Low": {
            "do": [
                "Nutrient-rich foods: zinc (nuts, seeds), vitamin C, protein.",
                "Sleep 7-8 hours daily.",
                "Manage stress (yoga, meditation).",
                "Check for HIV, hepatitis, autoimmune diseases if recurrent."
            ],
            "dont": [
                "Consume excessive processed junk food.",
                "Chronic alcohol consumption.",
                "Ignore recurrent infections."
            ],
            "situations": {
                "Mild": "Lifestyle changes; retest.",
                "Viral infection (acute)": "Rest; retest after recovery.",
                "HIV/immunodeficiency": "Infectious disease specialist.",
                "Steroid use": "Review with doctor.",
                "Autoimmune": "Rheumatologist consult."
            },
            "red_flags": [
                "Recurrent severe infections",
                "Unexplained weight loss",
                "Persistent fever",
                "Swollen lymph nodes >2 weeks"
            ],
            "lifestyle": "Sleep, stress management, balanced diet, regular exercise."
        },
        "High": {
            "do": [
                "Stay hydrated.",
                "Eat light, easily digestible meals.",
                "Allow body to recover from viral exposure.",
                "Repeat CBC after 2-4 weeks."
            ],
            "dont": [
                "Overwork or ignore persistent body aches.",
                "Ignore cold symptoms lasting >2 weeks.",
                "Consume alcohol/smoke."
            ],
            "situations": {
                "Viral infection": "Supportive care; retest.",
                "Chronic lymphocytic leukemia": "Hematologist/oncologist.",
                "Tuberculosis": "Chest X-ray, sputum test.",
                "Stress": "Lifestyle changes.",
                "Smoking": "Quit."
            },
            "red_flags": [
                "Persistent fever >2 weeks",
                "Night sweats",
                "Weight loss",
                "Painless swollen lymph nodes"
            ],
            "lifestyle": "Hydration, rest, balanced diet, no smoking/alcohol."
        }
    },

    "Platelet Count": {
        "Low": {
            "do": [
                "Consume papaya leaf extract, kiwi, pomegranate.",
                "Bed rest; avoid injury.",
                "Monitor for unusual bruising/bleeding.",
                "Use soft toothbrush; avoid sharp objects.",
                "Follow doctor's advice on platelet transfusion if <20,000/µL."
            ],
            "dont": [
                "Take blood-thinning painkillers (Aspirin, Ibuprofen) without consultation.",
                "Play contact sports.",
                "Consume alcohol.",
                "Ignore bleeding gums or nosebleeds."
            ],
            "situations": {
                "Mild (100-150k)": "Monitor; avoid injury.",
                "Moderate (50-100k)": "Doctor consult; investigate cause.",
                "Severe (20-50k)": "Urgent care; may need treatment.",
                "Critical (<20k)": "Hospitalization; transfusion may be needed.",
                "Dengue": "Hospital monitoring; hydration.",
                "ITP": "Hematologist; steroids/IVIG."
            },
            "red_flags": [
                "Bleeding gums/nose",
                "Blood in urine/stool",
                "Petechiae (pinpoint red spots)",
                "Severe headache (brain bleed risk)"
            ],
            "lifestyle": "Avoid injury, no alcohol, soft diet, regular monitoring."
        },
        "High": {
            "do": [
                "Stay actively hydrated.",
                "Light physical movement to support circulation.",
                "Treat underlying cause (infection, iron deficiency, inflammation).",
                "Repeat CBC after treatment."
            ],
            "dont": [
                "Stay sedentary for long hours.",
                "Consume high-sodium foods.",
                "Ignore risk of clotting."
            ],
            "situations": {
                "Reactive thrombocytosis": "Treat infection/inflammation; retest.",
                "Iron deficiency": "Iron supplementation.",
                "Essential thrombocythemia": "Hematologist; may need medication.",
                "Post-splenectomy": "Monitor; low-dose aspirin if advised.",
                "Cancer": "Oncologist consult."
            },
            "red_flags": [
                "Chest pain",
                "Leg swelling/pain",
                "Severe headache",
                "Vision changes"
            ],
            "lifestyle": "Hydration, movement, low-sodium diet, regular follow-up."
        }
    },

    "HCT / Hematocrit": {
        "Low": {
            "do": [
                "Boost dietary iron and vitamin C.",
                "Consult doctor if fatigue persists.",
                "Check for chronic blood loss.",
                "Treat underlying anemia cause."
            ],
            "dont": [
                "Engage in heavy workouts when dizzy/lightheaded.",
                "Ignore symptoms of anemia.",
                "Skip meals."
            ],
            "situations": {
                "Mild": "Dietary changes; retest.",
                "Moderate": "Doctor consult; supplements.",
                "Severe": "Urgent care; transfusion may be needed.",
                "Pregnancy": "Monitor; iron supplementation.",
                "Chronic disease": "Treat underlying cause."
            },
            "red_flags": [
                "Breathlessness at rest",
                "Chest pain",
                "Fainting",
                "Rapid heartbeat"
            ],
            "lifestyle": "Iron-rich diet, adequate rest, avoid over-exertion."
        },
        "High": {
            "do": [
                "Correct dehydration immediately with water/electrolytes.",
                "Check for sleep apnea, high altitude, smoking.",
                "Consider blood donation if eligible.",
                "Treat underlying heart/lung/kidney disease."
            ],
            "dont": [
                "Neglect chronic snoring or sleep apnea signs.",
                "Ignore high-altitude acclimatization.",
                "Smoke."
            ],
            "situations": {
                "Dehydration": "Rehydrate; retest.",
                "Sleep apnea": "Sleep study; CPAP.",
                "Polycythemia": "Hematologist; phlebotomy.",
                "High altitude": "Acclimatize.",
                "Smoking": "Quit."
            },
            "red_flags": [
                "Chest pain",
                "Shortness of breath",
                "Severe headache",
                "Vision changes"
            ],
            "lifestyle": "Hydration, no smoking, regular cardiovascular check-ups."
        }
    },

    "MPV - Mean Platelet Volume": {
        "Low": {
            "do": [
                "Balanced diet rich in leafy greens.",
                "Attend routine follow-up tests.",
                "Monitor for bleeding/bruising.",
                "Check for bone marrow disorders if persistent."
            ],
            "dont": [
                "Ignore delayed blood clotting or prolonged bleeding from minor cuts.",
                "Take blood thinners without advice.",
                "Ignore easy bruising."
            ],
            "situations": {
                "Mild": "Monitor; retest.",
                "Moderate": "Doctor consult; investigate cause.",
                "Severe": "Hematologist; bone marrow test may be needed.",
                "Medication-induced": "Review medications.",
                "Bone marrow disorder": "Specialist care."
            },
            "red_flags": [
                "Prolonged bleeding from cuts",
                "Easy bruising",
                "Nosebleeds/gum bleeding",
                "Blood in urine/stool"
            ],
            "lifestyle": "Avoid injury, balanced diet, regular follow-up."
        },
        "High": {
            "do": [
                "Heart-friendly low-fat diet.",
                "Stay physically active.",
                "Annual cardiovascular check-ups.",
                "Treat underlying inflammation/infection."
            ],
            "dont": [
                "Smoke.",
                "Take trans-fats.",
                "Skip annual health check-ups."
            ],
            "situations": {
                "Mild": "Lifestyle changes; retest.",
                "Moderate": "Doctor consult; cardiovascular risk assessment.",
                "Severe": "Hematologist/cardiologist; investigate clotting disorders.",
                "Inflammation": "Treat cause.",
                "Medication": "Review with doctor."
            },
            "red_flags": [
                "Chest pain",
                "Shortness of breath",
                "Leg swelling/pain",
                "Sudden weakness/numbness"
            ],
            "lifestyle": "Low-fat diet, exercise, no smoking, regular check-ups."
        }
    }
}

# 4. Helper Function: OpenRouter AI Client
def get_ai_dual_analysis(messages, model, api_key):
    """Calls OpenRouter API and returns full response text."""
    if not api_key or not api_key.strip():
        return "ERROR: OpenRouter API key nahi mili. Kripya environment variable ya .env file me OPENROUTER_API_KEY set karein."
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "CBC Medical Report Analyzer"
    }
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "temperature": 0.6,
        "max_tokens": 3000
    }
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            err_msg = f"API Error (HTTP {response.status_code}): {response.text}"
            try:
                err_data = response.json()
                if "error" in err_data:
                    err_msg = err_data["error"].get("message", err_msg)
            except Exception:
                pass
            return f"ERROR: {err_msg}"

        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        return f"ERROR: Connection Error - {str(e)}"


# 5. Define CBC Parameters with Values & 'Don't know' Flags
cbc_parameters = [
    {
        "name": "Hemoglobin",
        "value": hb,
        "is_unknown": hb_unk,
        "display_value": f"{hb:.1f} g/dL" if not hb_unk else "Not Provided",
        "min": 13.5 if patient_gender == "Male" else 12.0,
        "max": 17.5 if patient_gender == "Male" else 15.5,
        "range": "13.5 - 17.5 g/dL" if patient_gender == "Male" else "12.0 - 15.5 g/dL"
    },
    {
        "name": "RBC Count",
        "value": rbc,
        "is_unknown": rbc_unk,
        "display_value": f"{rbc:.2f} million/mcL" if not rbc_unk else "Not Provided",
        "min": 4.5 if patient_gender == "Male" else 4.0,
        "max": 5.9 if patient_gender == "Male" else 5.2,
        "range": "4.5 - 5.9 million/mcL" if patient_gender == "Male" else "4.0 - 5.2 million/mcL"
    },
    {
        "name": "WBC Count",
        "value": wbc,
        "is_unknown": wbc_unk,
        "display_value": f"{wbc:,} /mcL" if not wbc_unk else "Not Provided",
        "min": 4000,
        "max": 11000,
        "range": "4,000 - 11,000 /mcL"
    },
    {
        "name": "Neutrophils",
        "value": neutrophils,
        "is_unknown": neutrophils_unk,
        "display_value": f"{neutrophils:.1f}%" if not neutrophils_unk else "Not Provided",
        "min": 40.0,
        "max": 70.0,
        "range": "40 - 70%"
    },
    {
        "name": "Lymphocytes",
        "value": lymphocytes,
        "is_unknown": lymphocytes_unk,
        "display_value": f"{lymphocytes:.1f}%" if not lymphocytes_unk else "Not Provided",
        "min": 20.0,
        "max": 40.0,
        "range": "20 - 40%"
    },
    {
        "name": "Platelet Count",
        "value": platelets,
        "is_unknown": platelets_unk,
        "display_value": f"{platelets:,} /mcL" if not platelets_unk else "Not Provided",
        "min": 150000,
        "max": 450000,
        "range": "150,000 - 450,000 /mcL"
    },
    {
        "name": "HCT / Hematocrit",
        "value": hct,
        "is_unknown": hct_unk,
        "display_value": f"{hct:.1f}%" if not hct_unk else "Not Provided",
        "min": 40.0 if patient_gender == "Male" else 36.0,
        "max": 50.0 if patient_gender == "Male" else 46.0,
        "range": "40 - 50%" if patient_gender == "Male" else "36 - 46%"
    },
    {
        "name": "MPV - Mean Platelet Volume",
        "value": mpv,
        "is_unknown": mpv_unk,
        "display_value": f"{mpv:.1f} fL" if not mpv_unk else "Not Provided",
        "min": 7.5,
        "max": 11.5,
        "range": "7.5 - 11.5 fL"
    }
]


# 6. Modal / Popup Dialog with Patient and Doctor Tabs (English Only + TXT Download)
@st.dialog("🤖 AI Medical Analysis & Consultation", width="large")
def show_ai_analysis_dialog(p_name, p_age, p_gender, params, model, api_key):
    """Displays AI Analysis in a popup modal with tabs for Patient and Doctor in English, with TXT download option."""
    # Check if all parameters are unknown
    if all(p["is_unknown"] for p in params):
        st.warning("⚠️ Sabhi parameters par **'Don't know / Not in report'** tick hai. Kripya report analyze karne ke liye kam se kam ek parameter provide karein.")
        return

    # Check cache in session state to avoid unnecessary re-calling
    cache_key = f"{p_name}_{p_age}_{p_gender}_" + "_".join(
        f"{p['name']}:{p['value']}:{p['is_unknown']}" for p in params
    )

    if "ai_modal_cache" not in st.session_state:
        st.session_state["ai_modal_cache"] = {}

    # Generate English Report if not cached
    if cache_key not in st.session_state["ai_modal_cache"]:
        # Prepare parameters summary
        param_lines = []
        for p in params:
            if p["is_unknown"]:
                param_lines.append(f"- **{p['name']}**: ❓ Not in report / Unknown by user")
            else:
                val = p["value"]
                min_v = p["min"]
                max_v = p["max"]
                if val < min_v:
                    p_stat = "LOW (Below normal range)"
                elif val > max_v:
                    p_stat = "HIGH (Above normal range)"
                else:
                    p_stat = "NORMAL (Within standard range)"
                param_lines.append(f"- **{p['name']}**: {p['display_value']} (Range: {p['range']}) -> Status: {p_stat}")

        params_text = "\n".join(param_lines)

        system_instruction = (
            "You are an expert hematologist and empathetic clinical medical AI consultant. "
            "Analyze the patient's Complete Blood Count (CBC) test parameters and provide TWO distinct sections in ENGLISH, "
            "separated EXACTLY by the delimiter '===DOCTOR_SECTION==='.\n\n"
            "--- SECTION 1 (BEFORE DELIMITER): FOR PATIENT (Clear, Patient-Friendly English) ---\n"
            "Provide compassionate, structured, easy-to-understand advice with the following specific headings:\n"
            "### 🩺 Health Issues & Symptoms (What's Wrong)\n"
            "- Explain in simple terms what abnormal parameters mean and what symptoms the patient might experience (e.g. fatigue, weakness, pale skin, cold hands/feet, lowered immunity).\n"
            "### 🥗 Diet & Nutrition Plan (What to Eat)\n"
            "- Detailed dietary recommendations: iron-rich foods (spinach, beetroot, pomegranate, lentils, dates, jaggery, red meat/poultry/eggs if non-vegetarian), Vitamin C rich foods (oranges, amla, lemon) to enhance iron absorption, protein and Vitamin B12 sources.\n"
            "### 🏃 Action Plan & Daily Habits (What to Do)\n"
            "- Practical daily steps: hydration (3-4 liters of water), adequate rest (7-8 hours of sleep), cooking in cast-iron utensils, gentle physical activity, and follow-up consultation schedule.\n"
            "### 🚫 Things to Avoid (What NOT to Do)\n"
            "- Clear precautions: Avoid drinking tea, coffee, or milk directly with iron-rich meals (they block iron absorption), avoid unprescribed high-dose iron supplements without checking ferritin, avoid heavy high-intensity workouts if feeling dizzy.\n"
            "### 🚨 Red Flag Warning Symptoms\n"
            "- Emergency danger signs requiring immediate hospital emergency evaluation (e.g. chest pain, shortness of breath at rest, fainting, black/tarry stools).\n\n"
            "===DOCTOR_SECTION===\n\n"
            "--- SECTION 2 (AFTER DELIMITER): FOR DOCTOR (Clinical & Technical Summary) ---\n"
            "Write in formal medical English for clinicians:\n"
            "### 📋 Clinical Hematology Summary\n"
            "- Pathophysiological evaluation, red cell indices (MCV/MCH/MCHC context), WBC differential, platelet dynamics.\n"
            "### 🔬 Differential Diagnosis\n"
            "- Top potential clinical etiologies based on the abnormal CBC pattern.\n"
            "### 🧪 Recommended Diagnostic Workup\n"
            "- Targeted follow-up tests (e.g. Serum Ferritin, TIBC, Iron saturation, Vitamin B12, Folate, Peripheral Blood Smear, Reticulocyte count).\n"
            "### 💊 Management & Monitoring Considerations\n"
            "- Evidence-based therapeutic considerations, dosing precautions, follow-up timeline."
        )

        user_content = f"""Patient Profile:
- Full Name: {p_name}
- Age: {p_age} years
- Gender: {p_gender}

CBC Test Parameters:
{params_text}

Please generate the detailed Patient Guide and Doctor Clinical Summary in English, separated by '===DOCTOR_SECTION==='."""

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_content}
        ]

        with st.spinner("🧠 AI is analyzing your report and preparing Patient & Doctor guidance..."):
            ai_raw_output = get_ai_dual_analysis(messages, model, api_key)
            if ai_raw_output.startswith("ERROR:"):
                st.error(ai_raw_output)
                return
            st.session_state["ai_modal_cache"][cache_key] = ai_raw_output

    english_report = st.session_state["ai_modal_cache"][cache_key]

    # Split into Patient and Doctor content
    if "===DOCTOR_SECTION===" in english_report:
        parts = english_report.split("===DOCTOR_SECTION===")
        patient_content = parts[0].strip()
        doctor_content = parts[1].strip()
    else:
        patient_content = english_report
        doctor_content = english_report

    # Prepare Downloadable TXT File Content
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt_download_content = f"""======================================================================
           COMPLETE BLOOD COUNT (CBC) - AI MEDICAL REPORT
======================================================================
Patient Name   : {p_name}
Age / Gender   : {p_age} years / {p_gender}
Report Date    : {timestamp_str}
AI Model       : {model}
======================================================================

[SECTION 1: PATIENT GUIDANCE REPORT]
----------------------------------------------------------------------
{patient_content}

======================================================================
[SECTION 2: DOCTOR'S CLINICAL SUMMARY]
----------------------------------------------------------------------
{doctor_content}

======================================================================
MEDICAL DISCLAIMER:
This AI report is generated for academic, educational, and informational
purposes only. It is NOT a substitute for professional clinical medical
advice, diagnosis, or treatment. Always consult a certified physician.
======================================================================
"""

    # Top Header Bar with Patient details and Save button
    col_info, col_save = st.columns([3, 1], vertical_alignment="center")
    with col_info:
        st.caption(f"👤 Patient: **{p_name}** ({p_gender}, {p_age} yrs) | Model: `{model}`")
    with col_save:
        st.download_button(
            label="💾 Save Report (.txt)",
            data=txt_download_content,
            file_name=f"CBC_Report_{p_name.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.write("")

    # Render Tabs inside the Popup Dialog (English Only)
    tab_patient, tab_doctor = st.tabs([
        "👤 For Patient (Personalized Health Guide)",
        "🩺 For Doctor (Clinical & Technical Summary)"
    ])

    with tab_patient:
        st.markdown(patient_content)
        st.divider()
        st.info("💡 **Patient Note:** This guide is for educational understanding and support. Please discuss with your doctor before making changes to medications or starting supplements.")

    with tab_doctor:
        st.markdown(doctor_content)
        st.divider()
        st.caption("⚖️ **Clinical Disclaimer:** AI-generated summary intended as clinical decision support. Always correlate with patient history, physical exam, and confirmatory laboratory assays.")


# 7. Main Input Page Button
st.write("")
if st.button("📊 Analyze Report", type="primary", use_container_width=True):
    st.session_state["show_results"] = True


# 8. Handling Rule-Based Report Analysis & Display
if st.session_state.get("show_results"):
    st.divider()

    # Results Heading with 'Analyze with AI' button on the right side!
    col_head, col_btn = st.columns([3, 1], vertical_alignment="center")
    with col_head:
        st.subheader(f"📊 Results for: {patient_name} ({patient_gender}, {patient_age} yrs)")
    with col_btn:
        if st.button("🤖 Analyze with AI", type="primary", use_container_width=True, key="btn_ai_modal"):
            show_ai_analysis_dialog(patient_name, patient_age, patient_gender, cbc_parameters, ai_model, ai_api_key)

    # Evaluate each parameter and display findings
    for param in cbc_parameters:
        name = param["name"]
        is_unk = param["is_unknown"]

        if is_unk:
            st.info(f"⚪ **{name}**: *Not in report / Don't know (Skipped)*")
            continue

        val = param["value"]
        min_v = param["min"]
        max_v = param["max"]
        disp_val = param["display_value"]
        range_str = param["range"]

        if val < min_v:
            status = "Low"
        elif val > max_v:
            status = "High"
        else:
            status = "Normal"

        msg = f"**{name}**: {disp_val} | Normal Range: {range_str} | Status: **{status}**"

        if status == "Normal":
            st.success(f"✅ {msg}")
        elif status == "Low":
            st.warning(f"⚠️ {msg}")
        else:
            st.error(f"🚨 {msg}")

        # Display Comprehensive Clinical Advice for abnormal results
        if status in ["Low", "High"] and name in HEALTH_ADVICE:
            advice = HEALTH_ADVICE[name].get(status)
            if advice:
                advice_lines = []

                # 1. Do's
                do_items = advice.get("do")
                if do_items:
                    advice_lines.append("> 🟢 **Do:**")
                    if isinstance(do_items, list):
                        for item in do_items:
                            advice_lines.append(f"> - {item}")
                    else:
                        advice_lines.append(f"> - {do_items}")

                # 2. Don'ts
                dont_items = advice.get("dont")
                if dont_items:
                    if advice_lines:
                        advice_lines.append(">")
                    advice_lines.append("> 🔴 **Don't:**")
                    if isinstance(dont_items, list):
                        for item in dont_items:
                            advice_lines.append(f"> - {item}")
                    else:
                        advice_lines.append(f"> - {dont_items}")

                # 3. Clinical Situations & Action Plan
                situations = advice.get("situations")
                if situations:
                    if advice_lines:
                        advice_lines.append(">")
                    advice_lines.append("> 📋 **Situations & Action Plan:**")
                    if isinstance(situations, dict):
                        for sit, sit_desc in situations.items():
                            advice_lines.append(f"> - **{sit}:** {sit_desc}")
                    elif isinstance(situations, list):
                        for sit in situations:
                            advice_lines.append(f"> - {sit}")
                    else:
                        advice_lines.append(f"> - {situations}")

                # 4. Red Flag Symptoms
                red_flags = advice.get("red_flags")
                if red_flags:
                    if advice_lines:
                        advice_lines.append(">")
                    advice_lines.append("> 🚨 **Red Flags (Seek Immediate Medical Care):**")
                    if isinstance(red_flags, list):
                        for flag in red_flags:
                            advice_lines.append(f"> - ⚠️ {flag}")
                    else:
                        advice_lines.append(f"> - ⚠️ {red_flags}")

                # 5. Lifestyle Guidance
                lifestyle = advice.get("lifestyle")
                if lifestyle:
                    if advice_lines:
                        advice_lines.append(">")
                    advice_lines.append("> 🌿 **Lifestyle Guidance:**")
                    if isinstance(lifestyle, list):
                        for ls in lifestyle:
                            advice_lines.append(f"> - {ls}")
                    else:
                        advice_lines.append(f"> - {lifestyle}")

                if advice_lines:
                    st.markdown("\n".join(advice_lines))
                st.write("")

# 9. Medical Disclaimer
st.divider()
st.info("📌 **Note:** This project is strictly for academic/educational purposes. Always consult a licensed medical professional for personal health concerns.")
