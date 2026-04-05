export async function getSnapshotByDate(selectedDate) {
  const response = await fetch(
    `http://127.0.0.1:8000/snapshot?date=${selectedDate}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch snapshot");
  }

  return await response.json();
}

export async function getJournalByDate(selectedDate) {
  const response = await fetch(
    `http://127.0.0.1:8000/journal?date=${selectedDate}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch journal");
  }

  return await response.json();
}