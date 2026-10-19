console.log("Charts.js loaded successfully");

const salesCanvas = document.getElementById("salesChart");

if (salesCanvas) {
    new Chart(salesCanvas, {
        type: "line",
        data: {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            datasets: [{
                label: "Monthly Sales",
                data: [12000, 15000, 18000, 14000, 22000, 25000],
                borderWidth: 3
            }]
        },
        options: {
            responsive: true
        }
    });
}

const categoryCanvas = document.getElementById("categoryChart");

if (categoryCanvas) {
    new Chart(categoryCanvas, {
        type: "bar",
        data: {
            labels: ["Technology", "Furniture", "Office Supplies"],
            datasets: [{
                label: "Sales by Category",
                data: [45000, 30000, 20000]
            }]
        },
        options: {
            responsive: true
        }
    });
}

const regionCanvas = document.getElementById("regionChart");

if (regionCanvas) {
    new Chart(regionCanvas, {
        type: "bar",
        data: {
            labels: ["South", "West", "North", "East"],
            datasets: [{
                label: "Sales by Region",
                data: [35000, 28000, 22000, 18000]
            }]
        },
        options: {
            indexAxis: "y",
            responsive: true
        }
    });
}