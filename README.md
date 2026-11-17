<p align="center">
  <img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/hero.gif" width="100%" alt="A pixel-art room in Rabat: an arched window showing the live weather over the Hassan Tower and the Oudaya kasbah, a monitor scrolling my latest commits, a brass lantern, a pot of mint tea, a homelab server and a sleeping cat." />
</p>

<p align="center">
  <sub>The window shows the weather in Rabat right now · the monitor scrolls my latest commits · every book on the shelf is a language I write · the clock shows when the room was last redrawn</sub>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/sabirbaichou/">LinkedIn</a> ·
  <a href="https://github.com/zehmbot?tab=repositories">Repositories</a>
</p>

<img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/about.gif" width="100%" alt="About: zehmbot, software engineer in Rabat, Morocco. PHP, Java, Python, Go, Laravel and Spring Boot." />

<img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/stats.gif" width="100%" alt="GitHub stats: commits, pull requests, stars and best streak." />

<!-- pixel:projects:start -->
<img src="https://raw.githubusercontent.com/zehmbot/zehmbot/output/projects.gif" width="100%" alt="Projects" />
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
