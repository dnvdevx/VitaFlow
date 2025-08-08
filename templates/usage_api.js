// Fetch and display usage rates for each item
async function fetchUsageRates() {
    const response = await fetch('/api/items');
    const items = await response.json();
    const usageRates = {};
    for (const item of items) {
        // Fetch usage for each item
        const usageResp = await fetch(`/api/usage/${item.id}`);
        const usage = await usageResp.json();
        usageRates[item.id] = usage.avg_daily_usage;
    }
    return usageRates;
}
