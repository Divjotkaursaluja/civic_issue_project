import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'
import { getStorage } from 'firebase/storage'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || 'AIzaSyCR7Egfv-H_tPjlohCZu4FW7O-6qk3sqyI',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 'crowdsourced-civic-lssue.firebaseapp.com',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || 'crowdsourced-civic-lssue',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || 'crowdsourced-civic-lssue.firebasestorage.app',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '557351724337',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '1:557351724337:web:74d9cb0f788353ce0cfc10',
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || 'G-4F41ZN15L1',
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)
export const db = getFirestore(app)
export const storage = getStorage(app)
