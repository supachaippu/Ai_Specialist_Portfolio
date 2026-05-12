import fs from 'fs';

const html = fs.readFileSync('opus_input.txt', 'utf8');
const folderName = "DJI_20260210_Regents";

const slides = [];
// Updated Regex to match the HTML structure provided
const clipRegex = /<div id="([^"]+)" class="[^"]+scroll-mt-10">[\s\S]*?<source src="([^"]+)"[\s\S]*?<span class="text-2xl font-bold text-success">(\d+)<\/span>[\s\S]*?<div class="text-foreground font-medium transition-colors inline"[^>]*>([^<]+)<\/div>/g;

let match;
while ((match = clipRegex.exec(html)) !== null) {
    slides.push({
        id: match[1],
        video_url: match[2],
        subject: match[4].trim(),
        caption: `Score: ${match[3]} | ${match[4].trim()}`,
        status: 'EDIT',
        folder_name: folderName
    });
}

console.log(JSON.stringify(slides));
