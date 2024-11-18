<script type="module">
  // Import the functions you need from the SDKs you need
  import { initializeApp } from "https://www.gstatic.com/firebasejs/11.0.2/firebase-app.js";
  import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.0.2/firebase-analytics.js";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  // For Firebase JS SDK v7.20.0 and later, measurementId is optional
  const firebaseConfig = {
    apiKey: "AIzaSyBFyfqEcTUqwxrrmoGq_Z166Mp4UDu3OYE",
    authDomain: "join-my.firebaseapp.com",
    projectId: "join-my",
    storageBucket: "join-my.firebasestorage.app",
    messagingSenderId: "901645233995",
    appId: "1:901645233995:web:6daefedf499746c4c702ce",
    measurementId: "G-6L4BS0W9VK"
  };

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  const analytics = getAnalytics(app);
</script>
