const {onRequest} = require("firebase-functions/v2/https");
const {onSchedule} = require("firebase-functions/v2/scheduler");
const {spawn} = require("child_process");
const functions = require("firebase-functions");

exports.scheduledFunction = onSchedule("every 1 hours", (event) => {
  return new Promise((resolve, reject) => {
    const env = {
      ...process.env,
      LINE_CHANNEL_ACCESS_TOKEN: functions.config().line.channel_access_token,
      LINE_CHANNEL_SECRET: functions.config().line.channel_secret,
    };

    const childProcess = spawn("python3", ["main.py"], {
      stdio: "inherit",
      env,
    });

    childProcess.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Process exited with code: ${code}`));
      }
    });
  });
});

exports.pythonApp = onRequest((req, res) => {
  const env = {
    ...process.env,
    LINE_CHANNEL_ACCESS_TOKEN: functions.config().line.channel_access_token,
    LINE_CHANNEL_SECRET: functions.config().line.channel_secret,
  };

  const childProcess = spawn("python3", ["main.py"], {
    stdio: "inherit",
    env,
  });

  childProcess.on("close", (code) => {
    if (code === 0) {
      res.status(200).send("Python script executed successfully");
    } else {
      res.status(500).send("Python script execution failed");
    }
  });
});

