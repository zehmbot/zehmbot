```php
<?php
namespace Zehmbot;

use DateTimeImmutable;

final readonly class Engineer
{
    public function __construct(
        public string $fullName   = 'Sabir Baichou',
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