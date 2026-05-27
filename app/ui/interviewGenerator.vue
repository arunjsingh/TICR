<template>
  <div class="min-h-screen bg-slate-900 text-slate-100 font-sans flex flex-col">
    <!-- Top Global App Bar -->
    <header class="bg-slate-950 border-b border-slate-800 px-6 py-4 flex justify-between items-center shadow-lg">
      <div class="flex items-center space-x-3">
        <span class="text-2xl">📝</span>
        <h1 class="text-xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
          TICR AI — Technical Interview Candidate Reviewer
        </h1>
      </div>
      <div class="flex items-center space-x-2 text-xs bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800">
        <span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
        <span class="text-slate-400 font-mono">Ollama: qwen2.5:14b</span>
      </div>
    </header>

    <!-- Main Workspace Grid Layout -->
    <main class="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 p-6 overflow-hidden">
      
      <!-- LEFT PANEL: CONFIGURATION & CONFIG INPUTS -->
      <section class="bg-slate-950 rounded-xl border border-slate-800 p-6 flex flex-col space-y-6 shadow-xl overflow-y-auto">
        <div>
          <h2 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
            <span>⚙️</span> Difficulty Distribution
          </h2>
          <div class="grid grid-cols-3 gap-4 bg-slate-900 p-4 rounded-lg border border-slate-800">
            <div class="flex flex-col items-center">
              <span class="text-xs text-emerald-400 font-medium mb-2">🟢 Easy</span>
              <div class="flex items-center space-x-2">
                <button @click="adjustDiff('easy', -1)" class="w-8 h-8 rounded bg-slate-800 hover:bg-slate-700 active:scale-95 transition flex items-center justify-center font-bold">-</button>
                <span class="w-6 text-center font-mono font-bold text-lg">{{ distribution.easy }}</span>
                <button @click="adjustDiff('easy', 1)" class="w-8 h-8 rounded bg-slate-800 hover:bg-slate-700 active:scale-95 transition flex items-center justify-center font-bold">+</button>
              </div>
            </div>
            <div class="flex flex-col items-center">
              <span class="text-xs text-amber-400 font-medium mb-2">🟡 Medium</span>
              <div class="flex items-center space-x-2">
                <button @click="adjustDiff('medium', -1)" class="w-8 h-8 rounded bg-slate-800 hover:bg-slate-700 active:scale-95 transition flex items-center justify-center font-bold">-</button>
                <span class="w-6 text-center font-mono font-bold text-lg">{{ distribution.medium }}</span>
                <button @click="adjustDiff('medium', 1)" class="w-8 h-8 rounded bg-slate-800 hover:bg-slate-700 active:scale-95 transition flex items-center justify-center font-bold">+</button>
              </div>
            </div>
            <div class="flex flex-col items-center">
              <span class="text-xs text-rose-400 font-medium mb-2">🔴 Hard</span>
              <div class="flex items-center space-x-2">
                <button @click="adjustDiff('hard', -1)" class="w-8 h-8 rounded bg-slate-800 hover:bg-slate-700 active:scale-95 transition flex items-center justify-center font-bold">-</button>
                <span class="w-6 text-center font-mono font-bold text-lg">{{ distribution.hard }}</span>
                <button @click="adjustDiff('hard', 1)" class="w-8 h-8 rounded bg-slate-800 hover:bg-slate-700 active:scale-95 transition flex items-center justify-center font-bold">+</button>
              </div>
            </div>
          </div>
          <p class="text-right text-xs text-slate-500 mt-2 font-mono">Total Expected: {{ totalExpected }} Questions</p>
        </div>

        <!-- Job Description Input Area with Dropzone -->
        <div class="flex-1 flex flex-col min-h-[220px]">
          <label class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2 flex justify-between items-center">
            <span class="flex items-center gap-2"><span>📋</span> Job Description 
            <!-- <span class="text-rose-500 text-xs">*Required</span> -->
          </span>
          </label>
          
          <!-- Dropzone Component Utility for JD -->
          <div 
            @dragover.prevent="jdDrag = true" 
            @dragleave="jdDrag = false" 
            @drop.prevent="handleFileDrop($event, 'jd')"
            :class="{'border-blue-500 bg-slate-900/80': jdDrag, 'border-slate-800 bg-slate-900' : !jdDrag}"
            class="border border-dashed rounded-t-lg p-3 text-center transition group relative flex flex-col items-center justify-center cursor-pointer"
          >
            <input type="file" accept=".txt,.pdf,.docx" @change="handleFileUpload($event, 'jd')" class="absolute inset-0 opacity-0 cursor-pointer" />
            <p class="text-xs text-slate-400 group-hover:text-slate-300">📁 Drag & drop or <span class="text-blue-400 underline">browse</span> (.txt, .pdf, .docx)</p>
          </div>

          <textarea 
            v-model="jobDescription"
            placeholder="Paste the technical system criteria or role documentation rules here..." 
            class="w-full flex-1 p-3 bg-slate-900 border-x border-b border-slate-800 rounded-b-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm text-slate-200 placeholder-slate-600 resize-none font-sans leading-relaxed"
          ></textarea>
        </div>

        <!-- Candidate Resume Input Area with Dropzone -->
        <div class="flex-1 flex flex-col min-h-[200px]">
          <label class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2 flex justify-between items-center">
            <span class="flex items-center gap-2"><span>📄</span> Candidate Resume <span class="text-slate-600 text-xs">(Optional)</span></span>
          </label>
          
          <!-- Dropzone Component Utility for Resume -->
          <div 
            @dragover.prevent="resumeDrag = true" 
            @dragleave="resumeDrag = false" 
            @drop.prevent="handleFileDrop($event, 'resume')"
            :class="{'border-blue-500 bg-slate-900/80': resumeDrag, 'border-slate-800 bg-slate-900' : !resumeDrag}"
            class="border border-dashed rounded-t-lg p-3 text-center transition group relative flex flex-col items-center justify-center cursor-pointer"
          >
            <input type="file" accept=".txt,.pdf,.docx" @change="handleFileUpload($event, 'resume')" class="absolute inset-0 opacity-0 cursor-pointer" />
            <p class="text-xs text-slate-400 group-hover:text-slate-300">📁 Drag & drop or <span class="text-blue-400 underline">browse</span> (.txt, .pdf, .docx)</p>
          </div>

          <textarea 
            v-model="resume"
            placeholder="Paste raw text resume context to explicitly customize targeted queries..." 
            class="w-full flex-1 p-3 bg-slate-900 border-x border-b border-slate-800 rounded-b-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm text-slate-200 placeholder-slate-600 resize-none font-sans leading-relaxed"
          ></textarea>
        </div>

        <!-- Submit Pipeline Action Trigger -->
        <button 
          @click="generatePack"
          :disabled="(!jobDescription.trim() && !resume.trim()) || isLoading"
          class="w-full py-3.5 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-600 font-semibold rounded-lg shadow-lg active:scale-[0.99] transition duration-150 flex items-center justify-center space-x-2 text-sm disabled:cursor-not-allowed"
        >
          <span v-if="isLoading" class="animate-spin border-2 border-slate-400 border-t-transparent rounded-full h-4 w-4 mr-1"></span>
          <span>{{ isLoading ? 'Processing Ollama Generation Matrix...' : '⚡ Generate Custom Interview Pack' }}</span>
        </button>
      </section>

      <!-- RIGHT PANEL: INTERVIEW QUESTIONS SYSTEM OUTPUT -->
      <section class="bg-slate-950 rounded-xl border border-slate-800 p-6 flex flex-col shadow-xl overflow-hidden">
        <div class="flex justify-between items-center mb-4 pb-2 border-b border-slate-800">
          <h2 class="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-2">
            <span>🤖</span> Generated Technical Evaluation
          </h2>
          
          <div class="flex items-center space-x-2" v-if="questions.length > 0">
            <button @click="exportAsText" class="px-2.5 py-1 text-xs bg-slate-900 border border-slate-800 hover:border-slate-700 rounded font-medium flex items-center gap-1 text-slate-300">
              <span>📄</span> .TXT
            </button>
            <button @click="exportAsDocx" class="px-2.5 py-1 text-xs bg-slate-900 border border-slate-800 hover:border-slate-700 rounded font-medium flex items-center gap-1 text-slate-300">
              <span>📝</span> .DOCX
            </button>
          </div>
        </div>

        <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center space-y-3">
          <div class="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p class="text-sm text-slate-500 font-mono animate-pulse">Running inferences inside qwen2.5:14b...</p>
        </div>

        <div v-else-if="questions.length === 0" class="flex-1 flex flex-col items-center justify-center text-slate-600 p-8 border border-dashed border-slate-800 rounded-lg bg-slate-900/50">
          <span class="text-4xl mb-2">⚡</span>
          <p class="text-sm text-center font-medium max-w-xs">Fill in your requirements or upload project files to populate your technical evaluation checklist.</p>
        </div>

        <div v-else class="flex-1 overflow-y-auto space-y-4 pr-1">
          <div 
            v-for="(item, index) in questions" 
            :key="index"
            class="p-4 bg-slate-900 border rounded-lg shadow-sm transition"
            :class="{
              'border-emerald-950/60 bg-gradient-to-br from-slate-900 to-emerald-950/10': item.difficulty === 'easy',
              'border-amber-950/60 bg-gradient-to-br from-slate-900 to-amber-950/10': item.difficulty === 'medium',
              'border-rose-950/60 bg-gradient-to-br from-slate-900 to-rose-950/10': item.difficulty === 'hard',
            }"
          >
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-mono font-semibold uppercase tracking-wider px-2 py-0.5 rounded"
                :class="{
                  'bg-emerald-500/10 text-emerald-400': item.difficulty === 'easy',
                  'bg-amber-500/10 text-amber-400': item.difficulty === 'medium',
                  'bg-rose-500/10 text-rose-400': item.difficulty === 'hard',
                }"
              >
                Q{{ index + 1 }} — {{ item.difficulty }}
              </span>
            </div>
            <p class="text-sm text-slate-200 font-medium mb-3 leading-relaxed select-text">{{ item.question }}</p>
            <div class="bg-slate-950/80 rounded p-3 border border-slate-800/60">
              <span class="block text-xs font-bold text-slate-500 uppercase tracking-wide mb-1 font-mono">✅ Ideal Answer:</span>
              <p class="text-xs text-slate-400 leading-relaxed select-text">{{ item.answer }}</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
<script setup>
import { ref, computed } from 'vue';
import axios from 'axios';
import * as mammoth from 'mammoth';
import * as pdfjsLib from 'pdfjs-dist';

// Set up the background worker path for PDF processing
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cloudflare.com{pdfjsLib.version}/pdf.worker.min.mjs`;

// Target Text Form State Variables
const jobDescription = ref('');
const resume = ref('');
const isLoading = ref(false);
const questions = ref([]);

// Drag Visual Micro-States
const jdDrag = ref(false);
const resumeDrag = ref(false);

const distribution = ref({ easy: 2, medium: 2, hard: 2 });
const totalExpected = computed(() => distribution.value.easy + distribution.value.medium + distribution.value.hard);

const adjustDiff = (type, amt) => {
  const newVal = distribution.value[type] + amt;
  if (newVal >= 0 && newVal <= 10) distribution.value[type] = newVal;
};

// --- FILE EXTRACTION ROUTINES ---

const handleFileDrop = (event, targetField) => {
  if (targetField === 'jd') jdDrag.value = false;
  if (targetField === 'resume') resumeDrag.value = false;
  
  const files = event.dataTransfer.files;
  if (files && files.length > 0) processInputFile(files[0], targetField);
};

const handleFileUpload = (event, targetField) => {
  const file = event.target.files[0];
  if (file) processInputFile(file, targetField);
};

const processInputFile = async (file, targetField) => {
  const extension = file.name.split('.').pop().toLowerCase();
  
  try {
    if (extension === 'txt') {
      const reader = new FileReader();
      reader.onload = (e) => assignExtractedText(e.target.result, targetField);
      reader.readAsText(file);
    } 
    else if (extension === 'docx') {
      const arrayBuffer = await file.arrayBuffer();
      // mammoth extracts raw clean text while discarding complex hidden layout XML
      const result = await mammoth.extractRawText({ arrayBuffer: arrayBuffer });
      assignExtractedText(result.value, targetField);
    } 
    else if (extension === 'pdf') {
      const arrayBuffer = await file.arrayBuffer();
      const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
      const pdf = await loadingTask.promise;
      let fullText = '';
      
      // Loop through every page to compile the full document text string
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map(item => item.str).join(' ');
        fullText += pageText + '\n';
      }
      
      assignExtractedText(fullText, targetField);
    } 
    else {
      alert('Unsupported format. Please upload a .txt, .pdf, or .docx file.');
    }
  } catch (err) {
    console.error('File parsing error:', err);
    alert('Failed to parse text from the uploaded file safely.');
  }
};

const assignExtractedText = (text, targetField) => {
  if (!text || !text.trim()) {
    alert('Warning: No readable text could be extracted from this document.');
    return;
  }
  if (targetField === 'jd') jobDescription.value = text.trim();
  if (targetField === 'resume') resume.value = text.trim();
};

// Built-in basic browser utility to strip text out of compressed OpenXML docx containers
const extractDocxTextNatively = async (arrayBuffer) => {
  const textDecoder = new TextDecoder('utf-8');
  const decodedContent = textDecoder.decode(new Uint8Array(arrayBuffer));
  const textRuns = decodedContent.match(/<w:t[^>]*>(.*?)<\/w:t>/g) || [];
  return textRuns.map(val => val.replace(/<[^>]+>/g, '')).join(' ');
};

// --- ENDPOINT TRANSMISSION & DOWNLOAD ENGINE ---

const generatePack = async () => {
  if (!jobDescription.value?.trim() && !resume.value?.trim()) return;
  isLoading.value = true;
  questions.value = [];
  
  try {
    // 1. Convert the JSON payload into a FormData object
    const formData = new FormData();
    
    // 2. Map the fields to match the exact names FastAPI expects
    formData.append('job_description_text', jobDescription.value);
    formData.append('resume_text', resume.value || '');
    formData.append('easy_count', distribution.value.easy);
    formData.append('medium_count', distribution.value.medium);
    formData.append('hard_count', distribution.value.hard);

    // 3. Send the FormData instance instead of the plain object
    const response = await axios.post('/api/interview/generate-custom-questions', formData);
    
    // 4. Update your questions state with the backend array
    // Note: Your FastAPI returns a schema with a .questions property
    questions.value = response.data.questions; 
    
  } catch (error) {
    console.error('Generation matrix exception:', error);
    // If FastAPI throws an input validation error (like text too short), show it
    const errorMsg = error.response?.data?.detail || 'Failed to safely extract questions.';
    alert(typeof errorMsg === 'string' ? errorMsg : 'Input validation failed.');
  } finally {
    isLoading.value = false;
  }
};


const exportAsText = () => {
  let content = `TICR AI — TECHNICAL EVALUATION PACK\nGenerated Questions\n===================================\n\n`;
  questions.value.forEach((q, i) => {
    content += `Q${i + 1} [${q.difficulty.toUpperCase()}]: ${q.question}\n\nIdeal Answer:\n${q.answer}\n\n-----------------------------------\n\n`;
  });
  triggerDownload(new Blob([content], { type: 'text/plain;charset=utf-8;' }), 'ticr-interview-pack.txt');
};

const exportAsDocx = () => {
  let htmlString = `
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://w3.org'>
    <head><title>Technical Interview Questions</title><style>body { font-family: Arial, sans-serif; }</style></head>
    <body>
      <h2>TICR AI - Technical Interview Pack</h2>
      <hr/>
  `;
  questions.value.forEach((q, i) => {
    htmlString += `<h3>Q${i + 1} (${q.difficulty.toUpperCase()})</h3><p><b>Question:</b> ${q.question}</p><p><b>Ideal Answer:</b> <i>${q.answer}</i></p><br/>`;
  });
  htmlString += `</body></html>`;
  triggerDownload(new Blob(['\ufeff' + htmlString], { type: 'application/msword' }), 'ticr-interview-pack.doc');
};

const triggerDownload = (blob, filename) => {
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.style.display = 'none';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
</script>
