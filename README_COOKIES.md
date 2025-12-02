
# How to Fix "YouTube is blocking requests from your IP"

If you see an error saying YouTube is blocking requests, you need to provide your browser cookies so the script can act as a logged-in user.

## Steps:

1.  **Install a "cookies.txt" extension** for your browser:
    *   Chrome: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflccfodihccpati)
    *   Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2.  **Go to YouTube**:
    *   Open [https://www.youtube.com](https://www.youtube.com) in your browser.
    *   Log in if you aren't already.

3.  **Export Cookies**:
    *   Click the extension icon.
    *   Export the cookies for the current tab (YouTube).
    *   Save the file as `cookies.txt`.

4.  **Place the file**:
    *   Move the `cookies.txt` file to the root of this project: `/Users/manishpriyadarshan/Codes/MyWriter/cookies.txt`

5.  **Retry**:
    *   Run your script again. The tool will automatically detect `cookies.txt` and use it.
