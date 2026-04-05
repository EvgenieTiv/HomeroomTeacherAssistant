const API_BASE_URL = "http://127.0.0.1:8000";

async function fetchJson(url, errorMessage) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(errorMessage);
  }

  return await response.json();
}

export async function getSnapshotByDate(selectedDate) {
  return fetchJson(
    `${API_BASE_URL}/snapshot?date=${selectedDate}`,
    "Failed to fetch snapshot"
  );
}

export async function getJournalByDate(selectedDate) {
  return fetchJson(
    `${API_BASE_URL}/journal?date=${selectedDate}`,
    "Failed to fetch journal"
  );
}

export async function getAiRecommendationsByDate(selectedDate, useLlm = false) {
  return fetchJson(
    `${API_BASE_URL}/recommendations_ai?date=${selectedDate}&use_llm=${useLlm}`,
    "Failed to fetch AI recommendations"
  );
}