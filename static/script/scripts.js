const monthYearHeader = document.getElementById("monthYear");
const daysContainer = document.querySelector(".days");
const prevMonthButton = document.getElementById("prevMonth");
const nextMonthButton = document.getElementById("nextMonth");
const selectedDateInput = document.getElementById("selectedDate");
const dateForm = document.getElementById("dateForm");

const currentDate = new Date();
let selectedDate = null;
let canGoNext = true; // Allow going to the next month initially

function updateCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    monthYearHeader.textContent = `${new Date(year, month).toLocaleDateString("en-US", { month: "long", year: "numeric" })}`;

    daysContainer.innerHTML = "";

    const firstDay = new Date(year, month, 1).getDay();
    const lastDay = new Date(year, month + 1, 0).getDate();

    for (let i = 0; i < firstDay; i++) {
        daysContainer.appendChild(document.createElement("div"));
    }

    for (let day = 1; day <= lastDay; day++) {
        const dayElement = document.createElement("div");
        dayElement.textContent = day;
        dayElement.classList.add("day");

        const currentMonthStart = new Date(year, month, 1);
        const currentDateObj = new Date(year, month, day);
        if (currentDateObj < currentMonthStart || currentDateObj > currentDate) {
            dayElement.classList.add("disabled");
        } else {
            dayElement.addEventListener("click", () => selectDate(year, month, day));
        }

        if (selectedDate && selectedDate.getDate() === day && selectedDate.getMonth() === month && selectedDate.getFullYear() === year) {
            dayElement.classList.add("selected");
        }

        daysContainer.appendChild(dayElement);
    }
}
const dropdownField = document.getElementById("dropdownField");
const paymentInfo = document.getElementById("payment-info");

dropdownField.addEventListener("change", () => {
if (dropdownField.value !== "option1") {
paymentInfo.style.display = "block";
} else {
paymentInfo.style.display = "none";
}
});
function selectDate(year, month, day) {
    selectedDate = new Date(year, month, day);
    updateCalendar();
    selectedDateInput.value = selectedDate.toISOString();
}

prevMonthButton.addEventListener("click", () => {
    if (!canGoNext) {
        currentDate.setMonth(currentDate.getMonth() - 1);
        updateCalendar();
        canGoNext = true; // Allow going to the next month again
        nextMonthButton.removeAttribute("disabled"); // Enable "Next" button
    }
});

nextMonthButton.addEventListener("click", () => {
    if (canGoNext) {
        currentDate.setMonth(currentDate.getMonth() + 1);
        updateCalendar();
        canGoNext = false; // Prevent going to the next month more than once
        prevMonthButton.removeAttribute("disabled"); // Enable "Previous" button
    }
});



updateCalendar();

function selectDate(year, month, day) {
    selectedDate = new Date(year, month, day);
    updateCalendar();
    selectedDateInput.value = selectedDate.toISOString();
}

dateForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (selectedDate) {
        const dropdownValue = document.getElementById("dropdownField").value;
    }
    
});