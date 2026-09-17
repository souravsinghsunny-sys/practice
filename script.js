const loadButton = document.getElementById("loadBtn");
const studentTable = document.getElementById("studentTable");
const studentRows = document.getElementById("studentRows");

const modal = document.getElementById("studentModal");
const openModalButton = document.getElementById("openModalBtn");
const closeModalButton = document.getElementById("closeModalBtn");

const studentForm = document.getElementById("studentForm");
const studentId = document.getElementById("studentId");

const modalTitle = document.getElementById("modalTitle");
const submitButton = document.getElementById("createBtn");
const statusMessage = document.getElementById("statusMsg");

let students = [];


// GET STUDENTS

function loadStudents() {

    studentTable.style.display = "table";

    studentRows.innerHTML = "Loading...";

    fetch("http://127.0.0.1:8000/students/")

        .then(function (response) {

            return response.json();

        })

        .then(function (data) {

            students = data.students;

            studentRows.innerHTML = "";

            for (let i = 0; i < students.length; i++) {

                let student = students[i];

                studentRows.innerHTML += `
                    <tr>
                        <td>${i + 1}</td>
                        <td>${student.name}</td>
                        <td>${student.age}</td>
                        <td>${student.email}</td>
                        <td>${student.course}</td>
                        <td>${student.city}</td>
                        <td class="action-cell">
                            <button class="btn-edit" onclick="editStudent(${i})">
                                Edit
                            </button>
                            <button class="btn-delete" onclick="deleteStudent(${student.id})">
                                Delete
                            </button>
                        </td>
                    </tr>
                `;
            }

        })

        .catch(function (error) {

            studentRows.innerHTML = "Error: " + error.message;

        });
}


// LOAD BUTTON

loadButton.addEventListener("click", function () {

    loadStudents();

});


// ADD STUDENT

openModalButton.addEventListener("click", function () {

    modal.style.display = "flex";

    modalTitle.innerText = "Add New Student";

    submitButton.innerText = "SUBMIT";

    studentForm.reset();

    studentId.value = "";

    statusMessage.innerText = "";

});


// EDIT STUDENT

function editStudent(index) {

    let student = students[index];

    studentId.value = student.id;

    document.getElementById("studentName").value = student.name;

    document.getElementById("studentAge").value = student.age;

    document.getElementById("studentEmail").value = student.email;

    document.getElementById("studentCourse").value = student.course;

    document.getElementById("studentCity").value = student.city;

    modalTitle.innerText = "Edit Student";

    submitButton.innerText = "UPDATE";

    modal.style.display = "flex";

}


// CLOSE MODAL

closeModalButton.addEventListener("click", function () {

    modal.style.display = "none";

});


// ADD OR UPDATE STUDENT

studentForm.addEventListener("submit", function (event) {

    event.preventDefault();


    let name = document.getElementById("studentName").value;

    let age = document.getElementById("studentAge").value;

    let email = document.getElementById("studentEmail").value;

    let course = document.getElementById("studentCourse").value;

    let city = document.getElementById("studentCity").value;


    let studentData = {

        name: name,
        age: Number(age),
        email: email,
        course: course,
        city: city

    };


    let url = "http://127.0.0.1:8000/students/";

    let method = "POST";


    if (studentId.value !== "") {

        url = "http://127.0.0.1:8000/students/" + studentId.value + "/";

        method = "PUT";

    }


    fetch(url, {

        method: method,

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(studentData)

    })

        .then(function (response) {

            return response.json();

        })

        .then(function (data) {

            statusMessage.innerText =
                data.message || "Student saved successfully!";

            statusMessage.style.color = "green";

            studentForm.reset();

            loadStudents();


            setTimeout(function () {

                modal.style.display = "none";

            }, 1000);

        })

        .catch(function (error) {

            statusMessage.innerText = "Error: " + error.message;

            statusMessage.style.color = "red";

        });

});


// DELETE STUDENT

function deleteStudent(id) {

    let confirmDelete = confirm("Are you sure you want to delete this student?");

    if (!confirmDelete) {
        return;
    }

    fetch("http://127.0.0.1:8000/students/" + id + "/", {
        method: "DELETE"
    })
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            alert(data.message || "Student deleted successfully!");
            loadStudents();
        })
        .catch(function (error) {
            alert("Error: " + error.message);
        });

}