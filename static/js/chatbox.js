 
 
 // Updated list of chatbot questions using objects for type differentiation.
    // The last question now requires a numeric input.
    const questions = [
        { text: `Hello, ${username}! Could you please share your age in years?`, type: "number" ,constraints: { min: 15, max: 120 } },
        { text: "Are you biologically male or female?", type: "button" },
        {text:"What is your Martial Status?",type:"button"},
        {text:"Can you let me know your current work type?",type:"button"},
        {text:"Could you describe your living environment?",type:"button"},
        {text:"What is your height in centimeters ?",type:"number", constraints: { min: 50, max: 250 }},
        {text:"What is your weight in kilograms ?",type:"number",constraints: { min: 20, max: 300 }},
        {text:"What is your smoking status?",type:"button"},
        { text: "Have you ever been diagnosed with high blood pressure or hypertension?", type: "button" },
        { text: "Could you please provide your average glucose level?", type: "number",constraints: { min: 40, max: 300 } },
        {text:"Lastly, have you ever been diagnosed with any heart-related conditions or heart disease?",type:"button"}
      ];
      console.log("User:", username);
      // Possible answers for button-based questions.
      const answers = {
        "Are you biologically male or female?": ["Male", "Female"],
        "Have you ever been diagnosed with high blood pressure or hypertension?": ["Yes","No"],
        "What is your Martial Status?":["Married","Single"],
        "Can you let me know your current work type?":["Employed","Government","Unemployed","Student/Dependent"],
        "Could you describe your living environment?":["Urban","Rural"],
        "What is your smoking status?":["Never Smoked","Former Smoker","Current Smoker"],
        "Lastly, have you ever been diagnosed with any heart-related conditions or heart disease?":["Yes","No"]
        // No preset answers for the numeric question.
      };
    
      let currentQuestionIndex = 0;
      const userResponses = {};
    
      // Start chatbot with the first question.
      function initiateChat() {
        addMessage(questions[currentQuestionIndex], "bot");
        displayOptions(questions[currentQuestionIndex]);
      }
    
      // Add a chat message. If the message is an object, display its text.
      function addMessage(message, sender) {
        const chatBox = document.getElementById("chatBox");
        const messageElement = document.createElement("div");
        messageElement.classList.add("chat-message", sender === "bot" ? "bot-message" : "user-message");
        messageElement.textContent = (typeof message === "object") ? message.text : message;
        chatBox.appendChild(messageElement);
        setTimeout(() => { chatBox.scrollTop = chatBox.scrollHeight; }, 100);
      }
    
      // Display answer options based on question type.
      function displayOptions(question) {
        const chatOptions = document.getElementById("chatOptions");
        chatOptions.innerHTML = "";
        
        // If the question requires a number input:
        if (typeof question === "object" && question.type === "number") {
          const inputField = document.createElement("input");
          inputField.type = "number";
          inputField.placeholder = "Enter number";
          inputField.id = "userInput";
          inputField.min = question.constraints.min;
          inputField.max = question.constraints.max;
          
          
    
          const errorDiv = document.createElement("div");
          errorDiv.id = "inputError";
          errorDiv.classList.add("error-message");

          const submitButton = document.createElement("button");
          submitButton.textContent = "Submit";
           // Single event listener for both 'click' and 'Enter' key
        const handleSubmit = (event) => {
          if (event.type === "click" || (event.type === "keypress" && event.key === "Enter")) {
              const value = Number(inputField.value);
              if (isNaN(value) || value < question.constraints.min || value > question.constraints.max) {
                  errorDiv.textContent = `Enter a value between ${question.constraints.min} and ${question.constraints.max}.`;
              } else {
                  errorDiv.textContent = "";
                  handleUserResponse(value);
              }
          }
      };
      submitButton.addEventListener("click", handleSubmit);
      inputField.addEventListener("keypress", handleSubmit);
      chatOptions.appendChild(errorDiv);

          chatOptions.appendChild(inputField);
          chatOptions.appendChild(submitButton);
        } else {
          // For button-based questions.
          const questionText = (typeof question === "object") ? question.text : question;
          answers[questionText].forEach(answer => {
            const button = document.createElement("button");
            button.textContent = answer;
            button.onclick = () => handleUserResponse(answer);
            chatOptions.appendChild(button);
          });
        }
      }
    
      // Typing Indicator shown while waiting for the next message.
      function showTypingIndicator() {
        const chatBox = document.getElementById("chatBox");
        const typingIndicator = document.createElement("div");
        typingIndicator.classList.add("chat-message", "bot-message", "typing-indicator");
        typingIndicator.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
        chatBox.appendChild(typingIndicator);
        chatBox.scrollTop = chatBox.scrollHeight;
        return typingIndicator;
      }
    
      // Handle the user's response.
      function handleUserResponse(answer) {
        addMessage(answer, "user");
        // Save the response using the question text as the key.
        const currentQuestion = questions[currentQuestionIndex];
        const key = (typeof currentQuestion === "object") ? currentQuestion.text : currentQuestion;
        userResponses[key] = answer;
        
        document.getElementById("chatOptions").innerHTML = "";
    
        const typingIndicator = showTypingIndicator();
    
        setTimeout(() => {
          typingIndicator.remove();
          currentQuestionIndex++;
          if (currentQuestionIndex < questions.length) {
            addMessage(questions[currentQuestionIndex], "bot");
            displayOptions(questions[currentQuestionIndex]);
          } else {
            document.getElementById("chatOptions").classList.add("hidden");
            sendResponsesToBackend();
          }
        }, 1500);
      }
      const redirectUrl = "/report";
      // Send user responses to the backend using the Fetch API.
      function sendResponsesToBackend() {
        // Replace this URL with your actual backend endpoint.
        const backendUrl = "/submit_chatbot";
    
        fetch(backendUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(userResponses)
        })
        .then(response => response.json())
        .then(data => {
          console.log("Responses sent successfully:", data);
          addMessage("Thank you for your responses!\n directing you to result page", "bot");
          //redirection
          setTimeout(() => {
            window.location.href = redirectUrl;
        }, 3000);
        })
        .catch(error => {
          console.error("Error sending responses:", error);
          addMessage("Oops! Something went wrong. Please try again later.", "bot");
        });
      }
    
      window.onload = initiateChat;
      const LogoutBtn = document.querySelector('.btnLogout')
      LogoutBtn.addEventListener('click',()=>{
        window.location.href = "/clear_session";
      })