\# Footprint Finder



A small tool that checks where a username exists across several websites,

and can guess likely usernames from a full name.



\## Why it exists

People can use it to see where their own username is taken and to spot

accounts that may be impersonating them.



\## How it works

\- The backend (Python, FastAPI) takes a username and checks profile URLs on

&#x20; GitHub, Reddit, Medium, Dev.to, GitLab, Codeberg, Bitbucket and Keybase in parallel.

\- Name search generates likely usernames (for example johnsmith, john.smith,

&#x20; jsmith) and checks each one.

\- The frontend (HTML/CSS/JS) shows results in a table.

\- Photo search links out to Google Lens and TinEye. No face recognition is built in.



\## Limits

\- A match means the username exists on a site, not that it belongs to the same person.

\- Name search results are weak matches, because many people share a name.

\- Some sites block automated checks, so they are left out of the list.



\## Privacy

\- Searches are not stored.

\- The page asks users to confirm they are searching for themselves or have permission.



\## Run it

1\. Install packages: `pip install fastapi uvicorn httpx`

2\. In the backend folder run: `uvicorn main:app --reload`

3\. Open frontend/index.html in a browser.

