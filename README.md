<h1 align="center">Bladwijzer - Open Source Readwise Alternative</h1>

<p align="center">
  <strong>Bladwijzer</strong> is an open-source project designed to automatically sync highlights from your Kindle to a database. Each day, you’ll receive a random highlight via email to help you recall more, and grow your knowledge over time.
</p>

## Features
<ul>
  <li><strong>Automatic Kindle Highlights Sync:</strong> Syncs your Kindle highlights effortlessly to a database.</li>
  <li><strong>Daily Email Reminders:</strong> Receive a random highlight in your inbox every day.</li>
  <li><strong>Completely Open Source:</strong> Free to use, modify, and improve.</li>
</ul>

## Requirements
<p>To use this project, you’ll need:</p>
<ol>
  <li>A server with Docker installed.</li>
  <li>A <a href="https://sendgrid.com/" target="_blank">SendGrid</a> account for email delivery.</li>
</ol>

## Setup Instructions
<p>Follow these simple steps to set up the project:</p>

<ol>
  <li>
    <strong>Clone the Repository</strong><br>
    <pre><code>git clone ttps://github.com/stijnchip/bladwijzer.git</code></pre>
  </li>
  <li>
    <strong>Edit the <code>.env</code> File</strong><br>
    Fill in the required settings in the <code>.env</code> file, including your SendGrid API key and other relevant configuration details.
  </li>
  <li>
    <strong>Run the Project with Docker</strong><br>
    Build and start the project using Docker Compose:<br>
    <pre><code>docker compose up --build -d</code></pre>
  </li>
</ol>

<h2>Contributing</h2>
<p>Contributions are welcome! Feel free to open issues, suggest features, or submit pull requests.</p>

<h2>License</h2>
<p>This project is licensed under the MIT License. See the <a href="LICENSE">LICENSE</a> file for details.</p>
