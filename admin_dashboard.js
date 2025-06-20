document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded and parsed - admin_dashboard.js running');

    // Sidebar menu interaction
    const topMenuItems = document.querySelectorAll('.top-menu li button[data-section]');
    const sections = document.querySelectorAll('.section');

    // Hide all sections except the one with 'active' class on page load
    sections.forEach(section => {
        if (!section.classList.contains('active')) {
            section.style.display = 'none';
        } else {
            section.style.display = 'block';
        }
    });

    topMenuItems.forEach(item => {
        item.addEventListener('click', (event) => {
            event.preventDefault();
            // Remove active class from all menu items
            topMenuItems.forEach(i => i.classList.remove('active'));
            // Add active class to clicked menu item
            item.classList.add('active');

            // Remove active class from all sections
            sections.forEach(section => {
                section.classList.remove('active');
                section.style.display = 'none';
            });

            // Add active class to the selected section
            const sectionId = item.getAttribute('data-section');
            const activeSection = document.getElementById(sectionId);
            if (activeSection) {
                activeSection.classList.add('active');
                activeSection.style.display = 'block';
            }
        });
    });

    /* Vehicle Type Chart */
    const vehicleTypeChartElement = document.getElementById('vehicleTypeChart');
    if (vehicleTypeChartElement) {
        console.log('Initializing Vehicle Type Chart');
        const ctx = vehicleTypeChartElement.getContext('2d');
        let vehicleTypes = {};
        try {
            vehicleTypes = JSON.parse(vehicleTypeChartElement.dataset.vehicleTypes);
        } catch (e) {
            console.error('Error parsing vehicleTypes JSON:', e);
        }
        const labels = Object.keys(vehicleTypes);
        const data = Object.values(vehicleTypes);
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Vehicles',
                    data: data,
                    backgroundColor: 'rgba(255, 111, 97, 0.8)',
                    borderColor: 'rgba(255, 111, 97, 1)',
                    borderWidth: 2,
                    hoverBackgroundColor: 'rgba(255, 111, 97, 1)',
                    hoverBorderColor: 'rgba(255, 111, 97, 1)',
                    borderSkipped: false,
                    barPercentage: 0.5,
                    categoryPercentage: 0.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleFont: { size: 16, weight: 'bold' },
                        bodyFont: { size: 14 }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#fff',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(255,255,255,0.15)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        precision: 0,
                        ticks: {
                            color: '#fff',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(255,255,255,0.15)'
                        }
                    }
                }
            }
        });
    } else {
        console.warn('Element with id "vehicleTypeChart" not found.');
    }

    /* Average Price Chart */
    const averagePriceChartElement = document.getElementById('averagePriceChart');
    if (averagePriceChartElement) {
        const ctx = averagePriceChartElement.getContext('2d');
        let averagePrices = {};
        try {
            averagePrices = JSON.parse(averagePriceChartElement.dataset.averagePrices);
            console.log('Parsed averagePrices:', averagePrices);
        } catch (e) {
            console.error('Error parsing averagePrices JSON:', e);
        }
        const labels = Object.keys(averagePrices);
        const data = Object.values(averagePrices);
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Average Price',
                    data: data,
                    fill: false,
                    borderColor: 'rgba(255, 202, 40, 0.8)',
                    backgroundColor: 'rgba(255, 202, 40, 0.5)',
                    tension: 0.3,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleFont: { size: 16, weight: 'bold' },
                        bodyFont: { size: 14 }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#fff',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(255,255,255,0.15)'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#fff',
                            font: {
                                size: 12,
                                weight: 'bold'
                            }
                        },
                        grid: {
                            color: 'rgba(255,255,255,0.15)'
                        }
                    }
                }
            }
        });
    } else {
        console.warn('Element with id "averagePriceChart" not found.');
    }

    /* New Time Series Chart with Days/Months/Years Data */
    const timeSeriesChartElement = document.getElementById('timeSeriesChart');
    if (timeSeriesChartElement) {
        const ctx = timeSeriesChartElement.getContext('2d');

        // Sample data for days, months, years
        const timeSeriesData = {
            days: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                data: [12, 19, 3, 5, 2, 3, 7]
            },
            months: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                data: [120, 190, 300, 500, 200, 300, 700, 650, 400, 450, 600, 700]
            },
            years: {
                labels: ['2018', '2019', '2020', '2021', '2022', '2023'],
                data: [1200, 1900, 3000, 5000, 2000, 3000]
            }
        };

        let currentRange = 'days';

        const chartConfig = {
            type: 'line',
            data: {
                labels: timeSeriesData[currentRange].labels,
                datasets: [{
                    label: 'Sample Data',
                    data: timeSeriesData[currentRange].data,
                    fill: false,
                    borderColor: 'rgba(255, 202, 40, 0.8)',
                    backgroundColor: 'rgba(255, 202, 40, 0.5)',
                    tension: 0.3,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleFont: { size: 16, weight: 'bold' },
                        bodyFont: { size: 14 }
                    }
                }
            }
        };

        let timeSeriesChart = new Chart(ctx, chartConfig);

        // Event listener for time range selector
        const timeRangeSelect = document.getElementById('timeRangeSelect');
        if (timeRangeSelect) {
            timeRangeSelect.addEventListener('change', (event) => {
                currentRange = event.target.value;
                timeSeriesChart.data.labels = timeSeriesData[currentRange].labels;
                timeSeriesChart.data.datasets[0].data = timeSeriesData[currentRange].data;
                timeSeriesChart.update();
            });
        }
    } else {
        console.warn('Element with id "timeSeriesChart" not found.');
    }

    /* Condition Chart */
    const conditionChartElement = document.getElementById('conditionChart');
    if (conditionChartElement) {
        const ctx = conditionChartElement.getContext('2d');
        let conditionCounts = {};
        try {
            conditionCounts = JSON.parse(conditionChartElement.dataset.conditionCounts);
        } catch (e) {
            console.error('Error parsing conditionCounts JSON:', e);
        }
        const labels = Object.keys(conditionCounts);
        const data = Object.values(conditionCounts);

        // Define distinct colors with gradient for 3D effect
        const backgroundColors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)'
        ];
        const borderColors = [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)'
        ];

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Vehicle Condition Distribution',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 2,
                    hoverOffset: 30, // for 3D-like popout effect
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#fff',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleFont: { size: 16, weight: 'bold' },
                        bodyFont: { size: 14 }
                    }
                }
            }
        });
    } else {
        console.warn('Element with id "conditionChart" not found.');
    }

    /* Battery Condition Chart */
    const batteryConditionChartElement = document.getElementById('batteryConditionChart');
    if (batteryConditionChartElement) {
        const ctx = batteryConditionChartElement.getContext('2d');
        let batteryConditionCounts = {};
        try {
            batteryConditionCounts = JSON.parse(batteryConditionChartElement.dataset.batteryConditionCounts);
        } catch (e) {
            console.error('Error parsing batteryConditionCounts JSON:', e);
        }
        const labels = Object.keys(batteryConditionCounts);
        const data = Object.values(batteryConditionCounts);

        // Define distinct colors with gradient for 3D effect
        const backgroundColors = [
            'rgba(255, 159, 64, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(54, 162, 235, 0.8)'
        ];
        const borderColors = [
            'rgba(255, 159, 64, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 205, 86, 1)',
            'rgba(54, 162, 235, 1)'
        ];

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Battery Condition Distribution',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 2,
                    hoverOffset: 30,
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#fff',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleFont: { size: 16, weight: 'bold' },
                        bodyFont: { size: 14 }
                    }
                }
            }
        });
    } else {
        console.warn('Element with id "batteryConditionChart" not found.');
    }

    /* Tyres Condition Chart */
    const tyresConditionChartElement = document.getElementById('tyresConditionChart');
    if (tyresConditionChartElement) {
        const ctx = tyresConditionChartElement.getContext('2d');
        let tyresConditionCounts = {};
        try {
            tyresConditionCounts = JSON.parse(tyresConditionChartElement.dataset.tyresConditionCounts);
        } catch (e) {
            console.error('Error parsing tyresConditionCounts JSON:', e);
        }
        const labels = Object.keys(tyresConditionCounts);
        const data = Object.values(tyresConditionCounts);

        // Define distinct colors with gradient for 3D effect
        const backgroundColors = [
            'rgba(255, 99, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(54, 162, 235, 0.8)'
        ];
        const borderColors = [
            'rgba(255, 99, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(54, 162, 235, 1)'
        ];

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Tyres Condition Distribution',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 2,
                    hoverOffset: 30,
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#fff',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleFont: { size: 16, weight: 'bold' },
                        bodyFont: { size: 14 }
                    }
                }
            }
        });
    } else {
        console.warn('Element with id "tyresConditionChart" not found.');
    }
/* Scrap Price Chart */
    const scrapPriceChartElement = document.getElementById('scrapPriceChart');
    if (scrapPriceChartElement) {
        const ctx = scrapPriceChartElement.getContext('2d');
        let scrapPrices = {};
        try {
            scrapPrices = JSON.parse(scrapPriceChartElement.dataset.scrapPrices);
        } catch (e) {
            console.error('Error parsing scrapPrices JSON:', e);
        }
        const labels = Object.keys(scrapPrices);
        const data = Object.values(scrapPrices);
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Scrap Metal Prices',
                    data: data,
                    backgroundColor: 'rgba(97, 181, 255, 0.8)',
                    borderColor: 'rgba(97, 181, 255, 1)',
                    borderWidth: 2,
                    borderSkipped: false,
                    barPercentage: 0.5,
                    categoryPercentage: 0.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#fff',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleFont: { size: 16, weight: 'bold' },
                        bodyFont: { size: 14 }
                    }
                }
            }
        });
    } else {
        console.warn('Element with id "scrapPriceChart" not found.');
    }
    /* Scrap Reason Chart */
    const scrapReasonChartElement = document.getElementById('scrapReasonChart');
    if (scrapReasonChartElement) {
        const ctx = scrapReasonChartElement.getContext('2d');
        let scrapReasonCounts = {};
        try {
            scrapReasonCounts = JSON.parse(scrapReasonChartElement.dataset.scrapReasonCounts);
        } catch (e) {
            console.error('Error parsing scrapReasonCounts JSON:', e);
        }
        const labels = Object.keys(scrapReasonCounts);
        const data = Object.values(scrapReasonCounts);

        // Define distinct colors with gradient for 3D effect
        const backgroundColors = [
            'rgba(102, 204, 255, 0.8)',
            'rgba(255, 153, 102, 0.8)',
            'rgba(153, 255, 153, 0.8)',
            'rgba(255, 102, 204, 0.8)'
        ];
        const borderColors = [
            'rgba(102, 204, 255, 1)',
            'rgba(255, 153, 102, 1)',
            'rgba(153, 255, 153, 1)',
            'rgba(255, 102, 204, 1)'
        ];

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Scrap Reason Distribution',
                    data: data,
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 2,
                    hoverOffset: 30,
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#fff',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        titleFont: { size: 16, weight: 'bold' },
                        bodyFont: { size: 14 }
                    }
                }
            }
        });
    } else {
        console.warn('Element with id "scrapReasonChart" not found.');
    }

    // Image enlarging for images with class 'clickable-image' using modal approach
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const modalClose = document.getElementById('modalClose');

    if (!modal) {
        console.error('Modal element with id "imageModal" not found');
    }
    if (!modalImg) {
        console.error('Modal image element with id "modalImage" not found');
    }
    if (!modalClose) {
        console.error('Modal close element with id "modalClose" not found');
    }

    document.querySelectorAll('img.clickable-image').forEach(img => {
        console.log('Attaching click event to image:', img.src);
        img.style.cursor = 'pointer';
        img.addEventListener('click', (event) => {
            event.preventDefault();
            console.log('Image clicked:', img.src);
            modal.style.display = 'flex';
            modal.style.justifyContent = 'center';
            modal.style.alignItems = 'center';
            modal.style.backdropFilter = 'blur(5px)';
            modal.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
            // Fix: Set modal image src to the full image URL, not the thumbnail src
            // Assuming thumbnails have smaller size, and full image URL is stored in data-full-src attribute
            const fullImageSrc = img.getAttribute('data-full-src') || img.src;
            modalImg.src = fullImageSrc;
        });
    });

    modalClose.addEventListener('click', () => {
        console.log('Modal close button clicked');
        modal.style.display = 'none';
        modalImg.src = '';
    });

    modal.addEventListener('click', (event) => {
        if (event.target === modal || event.target === modalImg) {
            console.log('Modal background or image clicked');
            modal.style.display = 'none';
            modalImg.src = '';
        }
    });
});
document.addEventListener('DOMContentLoaded', function() {
    // Reinspection status dropdown and email modal handling
    const reinspectionDropdowns = document.querySelectorAll('.reinspection-status-dropdown');
    const emailModal = document.getElementById('reinspectionEmailModal');
    const emailForm = document.getElementById('reinspectionEmailForm');
    const emailUsernameInput = document.getElementById('emailUsername');
    const emailVehicleNumberInput = document.getElementById('emailVehicleNumber');
    const emailStatusInput = document.getElementById('emailStatus');
    const emailContentTextarea = document.getElementById('emailContent');
    const cancelEmailButton = document.getElementById('cancelEmailButton');

    function getEmailTemplate(status, username, amount) {
        if (status === 'Approved') {
            return `CONGRATS ${username.toUpperCase()}, YOUR REQUEST FOR REINSPECTION IS APPROVED.\n\n` +
                `THIS IS YOUR NEW ESTIMATED PRICE: ₹${amount || '[Enter Amount]'}.\n\n` +
                `FOR VEHICLE PICKUP, PLEASE REVERT BACK BY FILLING THE FOLLOWING DETAILS:\n` +
                `NAME:\nADDRESS:\nPHONE NUMBER:\nTIME SLOT:\n\n` +
                `Thank you.`;
        } else if (status === 'Rejected') {
            return `SORRY ${username.toUpperCase()}, YOUR REQUEST FOR REINSPECTION IS BEING REJECTED.\n\n` +
                `Thank you.`;
        }
        return '';
    }

    reinspectionDropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', (event) => {
            const selectedStatus = event.target.value;
            const username = event.target.getAttribute('data-username');
            const vehicleNumber = event.target.getAttribute('data-vehicle-number');

            if (selectedStatus === 'Pending') {
                // Do nothing or reset if needed
                return;
            }

            // Pre-fill email content
            let amount = '';
            if (selectedStatus === 'Approved') {
                amount = '[Enter Amount]';
            }
            const emailTemplate = getEmailTemplate(selectedStatus, username, amount);

            // Set form values
            emailUsernameInput.value = username;
            emailVehicleNumberInput.value = vehicleNumber;
            emailStatusInput.value = selectedStatus;
            emailContentTextarea.value = emailTemplate;

            // Show modal
            if (emailModal) {
                emailModal.style.display = 'block';
            } else {
                console.error('Email modal element not found');
            }

            // Reset dropdown to previous value until email is sent
            event.target.value = 'Pending';
        });
    });

    cancelEmailButton.addEventListener('click', () => {
        emailModal.style.display = 'none';
        location.reload();
    });

    emailForm.addEventListener('submit', (event) => {
        event.preventDefault();

        const formData = new FormData(emailForm);
        const data = {
            username: formData.get('username'),
            vehicle_number: formData.get('vehicle_number'),
            status: formData.get('status'),
            email_content: formData.get('email_content')
        };

        fetch('/api/send_reinspection_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).then(response => {
            if (response.ok) {
                alert('Email sent and status updated successfully.');
                emailModal.style.display = 'none';
                // Replace dropdown with locked "Completed" text
                const dropdowns = document.querySelectorAll('.reinspection-status-dropdown');
                dropdowns.forEach(dropdown => {
                    const username = dropdown.getAttribute('data-username');
                    const vehicleNumber = dropdown.getAttribute('data-vehicle-number');
                    if (username === data.username && vehicleNumber === data.vehicle_number) {
                        const parentTd = dropdown.parentElement;
                        if (parentTd) {
                            parentTd.textContent = 'Completed';
                        }
                    }
                });
            } else {
                alert('Failed to send email or update status.');
            }
        }).catch(error => {
            console.error('Error sending email:', error);
            alert('Error sending email.');
        });
    });
});
