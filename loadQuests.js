const fs = require('fs');

function readFile(path) {
    const text = fs.readFileSync(path, 'utf-8', (err, data) => {
        if (err) {
            console.error(err);
            return;
        }
        return data;
    });
    return text;
}

const rawText = readFile('./quests.txt');
const quests = JSON.parse(rawText);

export default quests;