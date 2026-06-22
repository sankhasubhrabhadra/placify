// Firebase v9 modular SDK
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { 
  getAuth, 
  GoogleAuthProvider, 
  signInWithPopup, 
  RecaptchaVerifier, 
  signInWithPhoneNumber,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// TODO: Replace with your actual Firebase Project Configuration
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Initialize Firebase
let app, auth;
try {
  app = initializeApp(firebaseConfig);
  auth = getAuth(app);
} catch (e) {
  console.warn("Firebase not properly configured yet. Using mock auth for UI testing.");
}

const googleProvider = new GoogleAuthProvider();

// Store the confirmation result from phone auth
window.confirmationResult = null;

// Mock function for when Firebase isn't configured yet
function mockRedirect() {
  console.log("Mock Auth Success. Redirecting...");
  setTimeout(() => { window.location.href = "index.html"; }, 1000);
}

// ----------------------
// LOGIN Logic
// ----------------------
window.handleLogin = async function(method) {
  if (method === 'google') {
    if (!auth) return mockRedirect();
    try {
      const result = await signInWithPopup(auth, googleProvider);
      console.log("Google Login Success", result.user);
      window.location.href = "index.html";
    } catch (error) {
      alert("Google Login Error: " + error.message);
    }
  } 
  else if (method === 'email') {
    const email = document.getElementById('login-email').value;
    const pass = document.getElementById('login-password').value;
    if (!auth) return mockRedirect();
    try {
      await signInWithEmailAndPassword(auth, email, pass);
      window.location.href = "index.html";
    } catch (error) {
      alert("Email Login Error: " + error.message);
    }
  }
  else if (method === 'phone') {
    const phone = document.getElementById('login-phone').value;
    if (!auth) {
      document.getElementById('btn-send-otp').style.display = 'none';
      document.getElementById('otp-section-login').style.display = 'block';
      return;
    }
    setupRecaptcha();
    try {
      const confirmationResult = await signInWithPhoneNumber(auth, phone, window.recaptchaVerifier);
      window.confirmationResult = confirmationResult;
      document.getElementById('btn-send-otp').style.display = 'none';
      document.getElementById('otp-section-login').style.display = 'block';
    } catch (error) {
      alert("SMS Error: " + error.message);
    }
  }
};

// ----------------------
// SIGNUP Logic
// ----------------------
window.handleSignup = async function(method) {
  const role = window.selectedRole || 'candidate'; // from signup.html
  console.log(`Signing up as: ${role}`);

  if (method === 'google') {
    if (!auth) return mockRedirect();
    try {
      const result = await signInWithPopup(auth, googleProvider);
      // Here you would usually send a request to your backend to save the user's role
      console.log("Google Signup Success", result.user);
      window.location.href = "index.html";
    } catch (error) {
      alert("Google Signup Error: " + error.message);
    }
  } 
  else if (method === 'email') {
    const email = document.getElementById('signup-email').value;
    const pass = document.getElementById('signup-password').value;
    const name = document.getElementById('signup-name-email').value;
    if (!auth) return mockRedirect();
    try {
      const result = await createUserWithEmailAndPassword(auth, email, pass);
      console.log("Email Signup Success", result.user);
      window.location.href = "index.html";
    } catch (error) {
      alert("Email Signup Error: " + error.message);
    }
  }
  else if (method === 'phone') {
    const phone = document.getElementById('signup-phone').value;
    const name = document.getElementById('signup-name-phone').value;
    if (!auth) {
      document.getElementById('btn-send-otp-signup').style.display = 'none';
      document.getElementById('otp-section-signup').style.display = 'block';
      return;
    }
    setupRecaptcha();
    try {
      const confirmationResult = await signInWithPhoneNumber(auth, phone, window.recaptchaVerifier);
      window.confirmationResult = confirmationResult;
      document.getElementById('btn-send-otp-signup').style.display = 'none';
      document.getElementById('otp-section-signup').style.display = 'block';
    } catch (error) {
      alert("SMS Error: " + error.message);
    }
  }
};

// ----------------------
// OTP Verification
// ----------------------
window.verifyOTP = async function(context) {
  const sectionId = context === 'login' ? 'otp-section-login' : 'otp-section-signup';
  const inputs = document.querySelectorAll(`#${sectionId} .otp-input`);
  let otp = '';
  inputs.forEach(input => otp += input.value);
  
  if (otp.length !== 6) {
    alert("Please enter a 6-digit code.");
    return;
  }

  if (!auth) return mockRedirect();

  try {
    const result = await window.confirmationResult.confirm(otp);
    console.log("Phone Auth Success", result.user);
    window.location.href = "index.html";
  } catch (error) {
    alert("Incorrect OTP: " + error.message);
  }
};

function setupRecaptcha() {
  if (!window.recaptchaVerifier) {
    window.recaptchaVerifier = new RecaptchaVerifier(auth, 'recaptcha-container', {
      'size': 'invisible'
    });
  }
}
