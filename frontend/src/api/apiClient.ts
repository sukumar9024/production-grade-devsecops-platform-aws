import axios from 'axios';

// No authenticated interceptors here: refreshing must never recursively refresh.
const authClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});
export default authClient;
