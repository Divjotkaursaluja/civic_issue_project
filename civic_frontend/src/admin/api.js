// src/admin/api.js
import axios from "axios";
import { API_BASE_URL } from "../apiBase";

const api = axios.create({
  baseURL: API_BASE_URL,// frontend proxy to Django (vite proxy) -> adjust if needed
  withCredentials: false, // set to true if you use session auth and CSRF
});

// --- API helpers ---
// Get counts per department (expected shape below)
export const getDepartmentCounts = async () => {
  return api.get("/api/complaints/counts/");
};

// List complaints for a department (dept_slug such as "streetlight" or "potholes")
export const listComplaintsByDepartment = async (deptSlug) => {
  return api.get(`/api/complaints/department/${deptSlug}/`);
};

// Update complaint status (id, newStatus: "Pending"|"In Progress"|"Solved")
export const updateComplaintStatus = (complaintId, status) => {
  return axios.post(
    `${API_BASE_URL}/api/complaints/${complaintId}/update-status/`,
    JSON.stringify({ status }),
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
};

// Fallback: fetch all complaints
export const listAllComplaints = async () => {
  const res = await axios.get(
    `${API_BASE_URL}/api/complaints/all/`
  );
  return res;   // IMPORTANT: return full response
};

export const getComplaintsByDepartment = (dept) => {
  return axios.get(`${API_BASE_URL}/api/complaints/department/${dept}/`);
};


export default api;
