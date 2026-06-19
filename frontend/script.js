async function login() {

    const email =
        document.getElementById("email").value;

    const password =
        document.getElementById("password").value;

    const response =
        await fetch(
            "http://192.168.49.2:32546/login",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                    "application/json"
                },
                body: JSON.stringify({
                    email,
                    password
                })
            }
        );

    const data =
        await response.json();
    console.log(data);

    localStorage.setItem(
        "token",
        data.access_token
    );

    alert("Logged in");
}

async function uploadFile() {

    const fileInput =
        document.getElementById("fileInput");

    const formData =
        new FormData();

    formData.append(
        "file",
        fileInput.files[0]
    );

    const token =
        localStorage.getItem("token");

    const response =
        await fetch(
            "http://192.168.49.2:31409/upload",
            {
                method: "POST",
                headers: {
                    Authorization:
                        `Bearer ${token}`
                },
                body: formData
            }
        );

    const data =
        await response.json();

    alert(data.message);

    loadFiles();
}

async function loadFiles() {

    const response =
        await fetch(
            "http://192.168.49.2:31409/files"
        );

    const files =
        await response.json();

    let html = "";

    files.forEach(file => {

        html += `
            <div>
                ${file.filename} (${file.status})

                <button onclick="showResult(${file.id})">
                    Show Result
                </button>

		<button onclick="showText(${file.id})">
		    Show Text
		</button>
		
		<button onclick="showAiAnalysis(${file.id})">
		    Show AI
		</button>
		
		<button onclick="downloadFile(${file.id})">
		    Download
		</button>
		
		<button onclick="deleteFile(${file.id})">
            Delete
        </button>   
            </div>
        `;
    });

    document.getElementById(
        "files"
    ).innerHTML = html;
}

async function showResult(fileId) {

    const response =
        await fetch(
            `http://192.168.49.2:31409/results/${fileId}`
        );

    const result =
        await response.json();

    document.getElementById(
        "result"
    ).innerHTML = `
        Pages: ${result.pages}<br>
        Words: ${result.words}<br>
        Symbols: ${result.symbols}
    `;
}

async function showText(fileId) {

    const response = await fetch(
        `http://192.168.49.2:31409/document/${fileId}`
    )

    const data = await response.json()

    document.getElementById("document").innerHTML =
        `<pre>${data.content}</pre>`
}

loadFiles();

async function showAiAnalysis(fileId) {

    const response = await fetch(
        `http://192.168.49.2:31409/ai-analysis/${fileId}`
    );

    const data = await response.json();

    document.getElementById("result").innerHTML =
        marked.parse(data.analysis);

    document.getElementById("result")
        .scrollIntoView({
            behavior: "smooth"
        });
}

function downloadFile(fileId) {

    window.open(
        `http://192.168.49.2:31409/download/${fileId}`,
        "_blank"
    );

}

async function deleteFile(fileId) {

    await fetch(
        `http://192.168.49.2:31409/files/${fileId}`,
        {
            method: "DELETE"
        }
    );

    loadFiles();
}