
const API_BASE_URL = "http://127.0.0.1:8000/api";

export const fetchScholarships = async (filters = {}) => {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      params.append(key, value);
    }
  });

  const queryString = params.toString();

  const url = queryString
    ? `${API_BASE_URL}/scholarships/?${queryString}`
    : `${API_BASE_URL}/scholarships/`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("Unable to fetch scholarships.");
  }

  return response.json();
};
