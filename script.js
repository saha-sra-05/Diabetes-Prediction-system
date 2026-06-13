
// ====================================
// HEALTH SCORE ANIMATION
// ====================================

window.onload = function(){

    animateRiskMeter();

    animateBoxes();

    speakHealthReport();
};

// ====================================
// RISK METER ANIMATION
// ====================================

function animateRiskMeter(){

    const fill = document.querySelector(
    ".risk-fill"
    );

    if(fill){

        const width = fill.style.width;

        fill.style.width = "0%";

        setTimeout(() => {

            fill.style.width = width;

        }, 300);
    }
}

// ====================================
// CARD ANIMATION
// ====================================

function animateBoxes(){

    const boxes = document.querySelectorAll(

        ".analysis-box, .recommend-box, .diet-box, .exercise-box, .future-box"

    );

    boxes.forEach((box,index) => {

        box.style.opacity = "0";

        box.style.transform =
        "translateY(20px)";

        setTimeout(() => {

            box.style.transition =
            "0.6s ease";

            box.style.opacity = "1";

            box.style.transform =
            "translateY(0px)";

        }, index * 200);

    });
}

// ====================================
// VOICE HEALTH REPORT
// ====================================

function speakHealthReport(){

    const result =
    document.querySelector(".main-result");

    if(result){

        let speech = new SpeechSynthesisUtterance(

            result.innerText

        );

        speech.lang = "en-US";

        speech.rate = 1;

        window.speechSynthesis.speak(
        speech
        );
    }
}

function askBot(){

    let question = document.getElementById(
        "user-question"
    ).value.toLowerCase();

    let response = "";

    // =====================================
    // HEALTH RESPONSE DATABASE
    // =====================================

    const responses = {

        diabetes:
        "Diabetes management requires healthy diet, exercise, glucose monitoring and regular medical checkups.",

        bloodpressure:
        "To control blood pressure: reduce salt intake, exercise regularly, reduce stress and monitor BP consistently.",

        glucose:
        "Maintaining balanced glucose levels through diet and physical activity is important for long-term health.",

        bmi:
        "Maintaining a healthy BMI reduces risks of diabetes, hypertension and cardiovascular disease.",

        exercise:
        "Regular walking, cardio, yoga and stretching improve overall metabolic and heart health.",

        food:
        "Healthy foods include vegetables, fruits, protein-rich foods, oats and reduced sugar intake.",

        heart:
        "Heart health improves with exercise, reduced smoking, stress control and balanced nutrition.",

        smoking:
        "Smoking increases risks of diabetes complications, stroke and heart disease. Quitting smoking is highly beneficial.",

        stress:
        "Stress management through sleep, meditation and exercise improves both mental and physical health.",

        sleep:
        "Good sleep supports healthy metabolism, blood pressure regulation and overall wellness.",

        water:
        "Proper hydration supports glucose balance, kidney function and cardiovascular health.",

        fever:
        "Persistent fever may indicate infection. Proper hydration and medical consultation are recommended.",

        cholesterol:
        "High cholesterol can increase heart disease risk. Healthy diet and exercise are recommended.",

        emergency:
        "If symptoms become severe or glucose levels are dangerously high, contact a healthcare professional immediately."

    };

    // =====================================
    // QUESTION MATCHING
    // =====================================

    if(

        question.includes("hello") ||
        question.includes("hi") ||
        question.includes("hey")

    ){

        response =
        "Hello! I am your AI Healthcare Assistant. Ask me anything related to health and wellness.";
    }

    else if(

        question.includes("diabetes") ||
        question.includes("sugar")

    ){

        response = responses.diabetes;
    }

    else if(

        question.includes("blood pressure") ||
        question.includes("bp") ||
        question.includes("pressure")

    ){

        response = responses.bloodpressure;
    }

    else if(

        question.includes("glucose")

    ){

        response = responses.glucose;
    }

    else if(

        question.includes("bmi") ||
        question.includes("weight") ||
        question.includes("obesity")

    ){

        response = responses.bmi;
    }

    else if(

        question.includes("exercise") ||
        question.includes("workout") ||
        question.includes("gym")

    ){

        response = responses.exercise;
    }

    else if(

        question.includes("food") ||
        question.includes("diet") ||
        question.includes("nutrition")

    ){

        response = responses.food;
    }

    else if(

        question.includes("heart")

    ){

        response = responses.heart;
    }

    else if(

        question.includes("smoking") ||
        question.includes("cigarette")

    ){

        response = responses.smoking;
    }

    else if(

        question.includes("stress") ||
        question.includes("anxiety")

    ){

        response = responses.stress;
    }

    else if(

        question.includes("sleep")

    ){

        response = responses.sleep;
    }

    else if(

        question.includes("water") ||
        question.includes("hydration")

    ){

        response = responses.water;
    }

    else if(

        question.includes("fever")

    ){

        response = responses.fever;
    }

    else if(

        question.includes("cholesterol")

    ){

        response = responses.cholesterol;
    }

    else if(

        question.includes("emergency") ||
        question.includes("critical")

    ){

        response = responses.emergency;
    }

    // =====================================
    // DEFAULT AI RESPONSE
    // =====================================

    else{

        response =
        "I can assist with diabetes, blood pressure, glucose, exercise, stress, heart health, sleep, diet and wellness guidance.";
    }

    // =====================================
    // DISPLAY CHAT
    // =====================================

    document.getElementById(
        "chat-area"
    ).innerHTML +=

    `

    <div class="chat-user">

        <b>You:</b> ${question}

    </div>

    <div class="chat-bot">

        <b>AI:</b> ${response}

    </div>

    `;
}



// ====================================
// VOICE INPUT
// ====================================

function startVoice(){

    // Browser support check

    if (!('webkitSpeechRecognition' in window)) {

        alert("Voice recognition not supported in this browser.");

        return;
    }

    const recognition =
    new webkitSpeechRecognition();

    recognition.lang = "en-US";

    recognition.continuous = false;

    recognition.interimResults = false;

    recognition.start();

    // When speech detected

    recognition.onresult = function(event){

        const transcript =
        event.results[0][0].transcript;

        document.getElementById(
            "user-question"
        ).value = transcript;
    };

    // Error handling

    recognition.onerror = function(event){

        alert(
        "Voice recognition error: "
        + event.error
        );
    };
}