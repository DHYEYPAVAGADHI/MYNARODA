import re

with open('templates/pages/landing.html', 'r') as f:
    content = f.read()

new_html = """
<section id="har-ghar-tiranga" class="relative overflow-hidden w-full bg-[#F3FBF5]">
  <!-- Accent bars -->
  <div class="absolute top-0 left-0 h-1 w-1/3 bg-[#FF9933] z-20"></div>
  <div class="absolute top-0 right-0 h-1 w-1/3 bg-[#138808] z-20"></div>
  <div class="absolute bottom-0 left-0 h-1 w-1/3 bg-[#FF9933] z-20"></div>
  <div class="absolute bottom-0 right-0 h-1 w-1/3 bg-[#138808] z-20"></div>

  <!-- Background Image & Overlay -->
  <div class="absolute inset-0 z-0">
    <img src="{% static 'images/har-ghar-tiranga.png' %}" alt="Har Ghar Tiranga City panorama" class="w-full h-full object-cover object-center">
    <div class="absolute inset-0" style="background: linear-gradient(90deg, rgba(255,255,255,0.78) 0%, rgba(255,255,255,0.38) 42%, rgba(255,255,255,0.08) 100%);"></div>
  </div>

  <div class="relative z-10 max-w-[1440px] mx-auto px-5 md:px-8 lg:px-16 lg:h-[800px] md:h-auto min-h-[700px] flex flex-col lg:flex-row items-center justify-between py-16 lg:py-0">
    
    <!-- Left Column (45%) -->
    <div class="w-full lg:w-[45%] flex flex-col justify-center reveal mb-12 lg:mb-0">
      <h2 class="font-serif text-[#0F172A] font-bold text-[42px] md:text-5xl lg:text-[68px] leading-tight mb-6 notranslate" translate="no">
        Har Ghar Tiranga
      </h2>
      <p class="font-sans text-[#1F2937] text-[18px] leading-[1.8] mb-10 max-w-[600px]">
        Alongside Green Naroda and Clean Naroda, we’re proud to run <strong>Har Ghar Tiranga</strong> across all of Naroda from <strong>11th to 15th August</strong> — hoisting the Indian national flag at every single home, and coming together for a massive <strong>Tiranga Yatra on 12th August</strong> through the streets of Naroda.
      </p>
      <button onclick="document.getElementById('registration-popup').classList.remove('hidden')"
        class="bg-[#FF7A00] hover:bg-[#E66E00] hover:-translate-y-1 text-white font-bold h-14 px-7 rounded-full shadow-lg transition-all flex items-center justify-center gap-3 w-fit text-lg">
        <i class="fa-solid fa-flag"></i> Join the Yatra
      </button>
    </div>

    <!-- Right Column (55%) -->
    <div class="w-full lg:w-[55%] flex flex-col sm:flex-row lg:flex-row lg:justify-end items-center sm:items-stretch lg:items-end lg:pb-16 gap-5 reveal reveal-delay-2 h-full justify-end">
      
      <!-- Card 1 -->
      <div class="bg-white/90 backdrop-blur-[10px] rounded-[28px] p-6 shadow-xl w-full sm:w-1/3 lg:w-[210px] h-[240px] flex flex-col items-center justify-center text-center transition-transform hover:-translate-y-2">
        <div class="w-[60px] h-[60px] rounded-full bg-[#FF9933]/10 flex items-center justify-center mb-5">
          <i class="fa-regular fa-calendar-days text-[#FF7A00] text-2xl"></i>
        </div>
        <h3 class="text-[#0F172A] font-bold text-[18px] mb-2 leading-tight">11–15 August</h3>
        <p class="text-[#6B7280] text-[14px]">Campaign Duration</p>
      </div>

      <!-- Card 2 -->
      <div class="bg-white/90 backdrop-blur-[10px] rounded-[28px] p-6 shadow-xl w-full sm:w-1/3 lg:w-[210px] h-[240px] flex flex-col items-center justify-center text-center transition-transform hover:-translate-y-2">
        <div class="w-[60px] h-[60px] rounded-full bg-[#15803D]/10 flex items-center justify-center mb-5">
          <i class="fa-solid fa-house-flag text-[#15803D] text-2xl"></i>
        </div>
        <h3 class="text-[#0F172A] font-bold text-[18px] mb-2 leading-tight">Every Home</h3>
        <p class="text-[#6B7280] text-[14px]">Flag Hoisted in the Nation</p>
      </div>

      <!-- Card 3 -->
      <div class="bg-white/90 backdrop-blur-[10px] rounded-[28px] p-6 shadow-xl w-full sm:w-1/3 lg:w-[210px] h-[240px] flex flex-col items-center justify-center text-center transition-transform hover:-translate-y-2">
        <div class="w-[60px] h-[60px] rounded-full bg-[#15803D]/10 flex items-center justify-center mb-5">
          <i class="fa-solid fa-people-group text-[#15803D] text-2xl"></i>
        </div>
        <h3 class="text-[#0F172A] font-bold text-[18px] mb-2 leading-tight">12 August</h3>
        <p class="text-[#6B7280] text-[14px]">Massive Tiranga Yatra</p>
      </div>

    </div>
  </div>
</section>
"""

# Pattern to replace everything from <section id="har-ghar-tiranga" ... to the end of the section
pattern = r'<section id="har-ghar-tiranga" class="relative overflow-hidden">[\s\S]*?</section>'

content = re.sub(pattern, new_html.strip(), content)

# Also update the next section background to match the prompt's instructions: "Keep the next section background #F3FBF5"
# It's currently bg-[#F0FDF4].
content = content.replace('<section id="progress" class="py-24 bg-[#F0FDF4]">', '<section id="progress" class="pt-16 pb-24 bg-[#F3FBF5]">')

with open('templates/pages/landing.html', 'w') as f:
    f.write(content)
print("Updated landing.html")
