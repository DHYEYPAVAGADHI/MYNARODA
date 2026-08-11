import re

with open('templates/pages/landing.html', 'r') as f:
    content = f.read()

new_html = """
    <!-- Header -->
    <div class="text-center mb-16 reveal">
      <div class="flex items-center justify-center gap-2 mb-4">
        <div class="inline-flex items-center gap-2 bg-[#E8F5EE] text-[#15803D] px-4 py-1.5 rounded-full">
          <i class="fa-solid fa-sitemap text-sm" aria-hidden="true"></i>
          <span class="font-bold text-xs tracking-widest uppercase">Organisation &amp; Committee</span>
        </div>
      </div>
      <h2 class="text-4xl md:text-5xl font-serif font-bold text-[#0F172A] mb-4">Main Planning Committee</h2>
      <p class="text-[#6B7280] text-base max-w-2xl mx-auto">Core leadership guiding the Green Naroda &bull; Clean Naroda mission</p>
    </div>

    <!-- Row 1: Standard leadership cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl mx-auto mb-16">
      <div class="ml-card reveal reveal-delay-1" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:120px;height:120px;">
          <i class="fa-solid fa-user-tie text-4xl text-[#9CA3AF]" aria-hidden="true"></i>
        </div>
        <div class="inline-block bg-[#15803D] text-white text-[10px] font-bold tracking-widest px-3 py-1 rounded-full mb-3 uppercase">President</div>
        <h3 class="ml-name text-[18px]">Dr. Payalben Kukrani</h3>
        <p class="ml-role">MLA, Naroda</p>
      </div>

      <div class="ml-card reveal reveal-delay-2" tabindex="0">
        <div class="ml-avatar mx-auto mb-5" style="width:120px;height:120px;">
          <i class="fa-solid fa-user-tie text-4xl text-[#9CA3AF]" aria-hidden="true"></i>
        </div>
        <div class="inline-block bg-[#15803D] text-white text-[10px] font-bold tracking-widest px-3 py-1 rounded-full mb-3 uppercase">Convener</div>
        <h3 class="ml-name text-[18px]">Shri Nikunj Rameshbhai Khakhi</h3>
        <p class="ml-role">President, Pratham Priority Club</p>
      </div>
    </div>

    <!-- Row 2: Co-conveners -->
    <div class="text-center mb-8 reveal">
      <span class="inline-block bg-[#E8F5EE] text-[#15803D] text-[11px] font-bold tracking-widest px-4 py-1.5 rounded-full uppercase">Co-Conveners</span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 reveal reveal-delay-1">
      <div class="bg-white border border-[#E5E7EB] rounded-[32px] p-6 shadow-sm hover:shadow-md transition-shadow text-center flex flex-col justify-center">
        <h3 class="text-lg font-bold text-[#0F172A] mb-1">Shri Kiran Raval</h3>
        <p class="text-[13px] text-[#6B7280] font-medium">President, BJP Naroda Ward</p>
      </div>
      <div class="bg-white border border-[#E5E7EB] rounded-[32px] p-6 shadow-sm hover:shadow-md transition-shadow text-center flex flex-col justify-center">
        <h3 class="text-lg font-bold text-[#0F172A] mb-1">Shri Nirav Joshi</h3>
        <p class="text-[13px] text-[#6B7280] font-medium">General Secretary, Naroda Ward</p>
      </div>
      <div class="bg-white border border-[#E5E7EB] rounded-[32px] p-6 shadow-sm hover:shadow-md transition-shadow text-center flex flex-col justify-center">
        <h3 class="text-lg font-bold text-[#0F172A] mb-1">Shri Gautam Patel</h3>
        <p class="text-[13px] text-[#6B7280] font-medium">General Secretary, Naroda Ward</p>
      </div>
      <div class="bg-white border border-[#E5E7EB] rounded-[32px] p-6 shadow-sm hover:shadow-md transition-shadow text-center flex flex-col justify-center">
        <h3 class="text-lg font-bold text-[#0F172A] mb-1">Shri Vipul Patel</h3>
        <p class="text-[13px] text-[#6B7280] font-medium">Chairman &amp; Municipal Councilor, Naroda AMC</p>
      </div>
      <div class="bg-white border border-[#E5E7EB] rounded-[32px] p-6 shadow-sm hover:shadow-md transition-shadow text-center flex flex-col justify-center">
        <h3 class="text-lg font-bold text-[#0F172A] mb-1">Shri Jayeshbhai Prajapati</h3>
        <p class="text-[13px] text-[#6B7280] font-medium">Municipal Councilor, Naroda AMC</p>
      </div>
      <div class="bg-white border border-[#E5E7EB] rounded-[32px] p-6 shadow-sm hover:shadow-md transition-shadow text-center flex flex-col justify-center">
        <h3 class="text-lg font-bold text-[#0F172A] mb-1">Shri Chandaben Patel</h3>
        <p class="text-[13px] text-[#6B7280] font-medium">Municipal Councilor, Naroda AMC</p>
      </div>
      <div class="bg-white border border-[#E5E7EB] rounded-[32px] p-6 shadow-sm hover:shadow-md transition-shadow text-center flex flex-col justify-center">
        <h3 class="text-lg font-bold text-[#0F172A] mb-1">Shri Divya Nikunj Khakhi</h3>
        <p class="text-[13px] text-[#6B7280] font-medium">Dy. Chairman &amp; Municipal Councilor, Naroda AMC</p>
      </div>
    </div>
"""

# We want to replace the <details> block starting at line 420.
pattern = r'<details class="reveal bg-white border border-\[#E5E7EB\] rounded-\[24px\] overflow-hidden shadow-sm">[\s\S]*?</details>'

def replacer(match):
    return new_html.strip()

new_content = re.sub(pattern, replacer, content)

if content == new_content:
    print("WARNING: Replacement failed! Pattern not found.")
else:
    with open('templates/pages/landing.html', 'w') as f:
        f.write(new_content)
    print("Updated landing.html")
