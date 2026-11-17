<p align="center">
  <img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/hero.gif" width="100%" alt="A pixel-art room in Rabat: an arched window showing the live weather over the Hassan Tower and the Oudaya kasbah, a monitor scrolling my latest commits, a brass lantern, a pot of mint tea, a homelab server and a sleeping cat." />
</p>

<p align="center">
  <sub>The window shows the weather in Rabat right now · the monitor scrolls my latest commits · every book on the shelf is a language I write · the clock shows when the room was last redrawn</sub>
</p>

<p align="center">
  <a href="https://github.com/lowlight-studio">Lowlight Studio</a> ·
  <a href="https://www.linkedin.com/in/sabirbaichou/">LinkedIn</a> ·
  <a href="https://github.com/zehmbot?tab=repositories">Repositories</a>
</p>

<img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/about.gif" width="100%" alt="About: zehmbot, software engineer in Rabat, Morocco, and founder of Lowlight Studio. PHP, Java, Python, Go, Laravel and Spring Boot." />

<a href="https://github.com/lowlight-studio"><img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/studio.gif" width="100%" alt="Lowlight Studio, the indie game studio I founded. Its ember candle logo flickers next to the name. Visit github.com/lowlight-studio." /></a>

<img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/stats.gif" width="100%" alt="GitHub stats: commits, pull requests, stars and best streak." />

<!-- pixel:projects:start -->
<img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/projects.gif" width="100%" alt="Projects" />

<p>
  <a href="https://github.com/zehmbot/virtus"><img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/project-1.gif" width="49%" alt="virtus: a crew of specialized AI agents that collaborate on your projects, then move on to the next." /></a>
  <a href="https://github.com/zehmbot/email-assistant-agent"><img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/project-2.gif" width="49%" alt="email-assistant-agent: An email assistant agent with authentication, dynamic tools and prompts (middleware), and human-in-the-loop approval before any email is sent, built with LangChain, LangGraph and Google Gemini." /></a>
  <a href="https://github.com/zehmbot/wedding-planner-agent"><img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/project-3.gif" width="49%" alt="wedding-planner-agent: A multi-agent AI wedding planner: a coordinator agent hands off flights (Kiwi MCP), venues (web search) and the playlist (SQL) to specialist agents, built with LangChain and Google Gemini." /></a>
  <a href="https://github.com/zehmbot/personal-chef-agent"><img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/project-4.gif" width="49%" alt="personal-chef-agent: An AI agent that turns your leftover ingredients into recipes, built with LangChain and Tavily web search" /></a>
</p>
<!-- pixel:projects:end -->

<img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/activity.gif" width="100%" alt="Contribution activity over the last year, with current and best streaks." />

<details>
<summary><code>$ cat whoami.php</code></summary>

```php
<?php
namespace Zehmbot;

final readonly class Engineer
{
    public function __construct(
        public string $fullName   = 'zehmbot',
        public string $city       = 'Rabat',
        public int    $age        = 24,
        public string $country    = 'Morocco',
        public string $email      = 'sabir.baichou@gmail.com',
        public array  $languages  = ['PHP', 'Java', 'Python', 'Go'],
        public array  $frameworks = ['Laravel', 'Spring Boot'],
    ) {
    }

    public function linkedIn(): string
    {
        return "https://www.linkedin.com/in/sabirbaichou/";
    }
}

$me = new Engineer();

```

</details>

<p align="center">
  <img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/footer.gif" width="100%" alt="Thanks for stopping by. The tea is always on." />
</p>

<!-- Every GIF above is drawn pixel by pixel by pixel/generate.py and refreshed by .github/workflows/pixel-profile.yml -->
