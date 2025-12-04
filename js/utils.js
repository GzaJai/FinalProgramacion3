export async function fetchWithCache(url, minutes = 5) {
  const key = `cache_${url}`;
  const cached = localStorage.getItem(key);

  if (cached) {
    const { timestamp, data } = JSON.parse(cached);

    const age = (Date.now() - timestamp) / 1000;
    if (age < minutes * 60) {
      return data; // devolver cache
    }
  }

  const res = await fetch(url);

  if (!res.ok) {
    throw new Error("HTTP error");
  }

  const data = await res.json();

  localStorage.setItem(key, JSON.stringify({
    timestamp: Date.now(),
    data
  }));

  return data;
}
