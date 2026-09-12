```php
<?php
namespace zehmbot;

final class Engineer
{
    public function __construct(
        public string $fullName = 'Sabir Baichou',
        public string $location = 'Morocco',
        public string $city = 'Rabat',
        public int $age = 24,
        public string $email = 'sabir.baichou@gmail.com',
        public array  $languages    = ['PHP', 'Laravel', 'Java', 'SpringBoot', 'Python', 'Go'],
    ) {}
}

$me = new Engineer();

```