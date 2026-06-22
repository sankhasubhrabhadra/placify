// Firebase v9 modular SDK
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { 
  getAuth, 
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged
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

// Mock function for when Firebase isn't configured yet
function mockRedirect() {
  console.log("Mock Auth Success. Redirecting...");
  setTimeout(() => { window.location.href = "index.html"; }, 1000);
}

// ----------------------
// LOGIN Logic
// ----------------------
window.handleLogin = async function(method) {
  const email = document.getElementById('login-email').value;
  const pass = document.getElementById('login-password').value;
  if (!auth) return mockRedirect();
  try {
    await signInWithEmailAndPassword(auth, email, pass);
    window.location.href = "index.html";
  } catch (error) {
    alert("Login Error: " + error.message);
  }
};

// ----------------------
// SIGNUP Logic
// ----------------------
window.handleSignup = async function(method) {
  const role = window.selectedRole || 'candidate'; // from signup.html
  console.log(`Signing up as: ${role}`);

  const email = document.getElementById('signup-email').value;
  const pass = document.getElementById('signup-password').value;
  const name = document.getElementById('signup-name-email').value;
  
  if (!auth) return mockRedirect();
  try {
    const result = await createUserWithEmailAndPassword(auth, email, pass);
    console.log("Signup Success", result.user);
    window.location.href = "index.html";
  } catch (error) {
    alert("Signup Error: " + error.message);
  }
};

// ----------------------
// LOGOUT Logic
// ----------------------
window.handleLogout = async function() {
  if (!auth) {
    window.location.href = "login.html";
    return;
  }
  try {
    await signOut(auth);
    window.location.href = "login.html";
  } catch (error) {
    alert("Logout Error: " + error.message);
  }
};

// ----------------------
// AUTH OBSERVER (Optional)
// ----------------------
// If you want to automatically redirect users who are NOT logged in back to login.html
if (auth) {
  onAuthStateChanged(auth, (user) => {
    const currentPage = window.location.pathname;
    const isAuthPage = currentPage.includes('login.html') || currentPage.includes('signup.html');
    
    if (user) {
      console.log("User is logged in:", user.email);
      // If they are on the login page but already logged in, redirect them to index
      if (isAuthPage) {
        window.location.href = "index.html";
      }
    } else {
      console.log("No user is logged in.");
      // If they are NOT on an auth page and NOT logged in, redirect to login
      if (!isAuthPage && currentPage !== "/" && currentPage !== "") {
        // window.location.href = "login.html"; // Uncomment to enforce login lock
      }
    }
  });
}
