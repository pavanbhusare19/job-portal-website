
const jobList = document.getElementById("jobList");
const jobForm = document.getElementById("jobForm");
const applicationList = document.getElementById("applicationList");

let allJobs = [];

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}

// Load jobs from Flask backend
async function loadJobs() {
    try {
        const response = await fetch("/api/jobs");

        if (!response.ok) throw new Error("Could not load jobs");

        allJobs = await response.json();
        displayJobs(allJobs);
    } catch (error) {
        jobList.innerHTML = "<p>Unable to load jobs. Please try again.</p>";
    }
}

// Display job cards
function displayJobs(jobs) {
    if (!jobs.length) {
        jobList.innerHTML = "<p>No jobs found. Try another search.</p>";
        return;
    }

    jobList.innerHTML = jobs.map(job => `
        <div class="job-card">
            <div class="job-info">
                <h3>${escapeHTML(job.title)}</h3>
                <h4>${escapeHTML(job.company)}</h4>
                <p>💼 ${escapeHTML(job.job_type)} &nbsp; | &nbsp;
                   📍 ${escapeHTML(job.location)}</p>
                <p>💰 ${escapeHTML(job.salary)}</p>
            </div>

            <div class="job-actions">
                <span class="job-type">${escapeHTML(job.job_type)}</span>
                <button class="apply-btn"
                    onclick="applyJob(${Number(job.id)})">
                    Apply Now
                </button>
            </div>
        </div>
    `).join("");
}

// Search jobs
function searchJobs() {
    const keyword = document.getElementById("searchInput")
        .value.toLowerCase().trim();

    const location = document.getElementById("locationInput")
        .value.toLowerCase().trim();

    const filteredJobs = allJobs.filter(job =>
        (job.title.toLowerCase().includes(keyword) ||
         job.company.toLowerCase().includes(keyword)) &&
        job.location.toLowerCase().includes(location)
    );

    displayJobs(filteredJobs);
}

// Popular search
function quickSearch(keyword) {
    document.getElementById("searchInput").value = keyword;
    searchJobs();
    document.getElementById("jobs").scrollIntoView({
        behavior: "smooth"
    });
}

// Apply for a job
async function applyJob(jobId) {
    const applicantName = prompt("Enter your full name:");

    if (!applicantName || !applicantName.trim()) {
        alert("Please enter your name.");
        return;
    }

    const email = prompt("Enter your email address:");

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
        alert("Please enter a valid email address.");
        return;
    }

    try {
        const response = await fetch("/api/applications", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                job_id: jobId,
                applicant_name: applicantName.trim(),
                email: email.trim()
            })
        });

        const result = await response.json();

        if (!response.ok) throw new Error(result.error || "Application failed");

        alert("Application submitted successfully!");
        loadApplications();
    } catch (error) {
        alert(error.message);
    }
}

// Post a new job
jobForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const jobData = {
        company: document.getElementById("company").value.trim(),
        title: document.getElementById("title").value.trim(),
        location: document.getElementById("jobLocation").value.trim(),
        salary: document.getElementById("salary").value.trim(),
        job_type: document.getElementById("jobType").value
    };

    try {
        const response = await fetch("/api/jobs", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(jobData)
        });

        const result = await response.json();

        if (!response.ok) throw new Error(result.error || "Could not post job");

        alert("Job posted successfully!");
        jobForm.reset();
        loadJobs();
    } catch (error) {
        alert(error.message);
    }
});

// Load submitted applications
async function loadApplications() {
    try {
        const response = await fetch("/api/applications");

        if (!response.ok) throw new Error("Could not load applications");

        const applications = await response.json();

        if (!applications.length) {
            applicationList.textContent = "No applications submitted yet.";
            return;
        }

        applicationList.innerHTML = applications.map(application => `
            <div class="application-item">
                <strong>${escapeHTML(application.applicant_name)}</strong>
                <p>${escapeHTML(application.job_title)} at
                   ${escapeHTML(application.company)}</p>
                <small>${escapeHTML(application.email)}</small>
            </div>
        `).join("");
    } catch (error) {
        applicationList.textContent = "Unable to load applications.";
    }
}

// Login demo
function showLogin() {
    alert("Welcome to JobConnect! Login functionality can be added next.");
}

// Initial loading
loadJobs();
loadApplications();
