// src/admin/api.js
import axios from "axios";
import { API_BASE_URL, apiUrl } from "../apiConfig";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
});

export const getDepartmentCounts = async () => {
  return api.get("/api/complaints/counts/");
};

export const listComplaintsByDepartment = async (deptSlug) => {
  return api.get(`/api/complaints/department/${deptSlug}/`);
};

export const updateComplaintStatus = (complaintId, status) => {
  return axios.post(
    apiUrl(`/api/complaints/${complaintId}/update-status/`),
    JSON.stringify({ status }),
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
};

export const listAllComplaints = async () => {
  const res = await axios.get(apiUrl("/api/complaints/all/"));
  return res;
};

export const getComplaintsByDepartment = (dept) => {
  return axios.get(apiUrl(`/api/complaints/department/${dept}/`));
};

export default api;
