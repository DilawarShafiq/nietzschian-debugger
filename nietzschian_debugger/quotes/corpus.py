"""Quote corpus for the Nietzschian Debugger."""

from __future__ import annotations

from ..types import Quote

QUOTES: list[Quote] = [
    # Nietzsche - avoidance
    Quote(text="He who has a why to live can bear almost any how.", philosopher="Friedrich Nietzsche", context="avoidance", source="Twilight of the Idols"),
    Quote(text="The higher we soar, the smaller we appear to those who cannot fly.", philosopher="Friedrich Nietzsche", context="avoidance", source="Beyond Good and Evil"),
    Quote(text="You must have chaos within you to give birth to a dancing star.", philosopher="Friedrich Nietzsche", context="avoidance", source="Thus Spoke Zarathustra"),
    Quote(text="There are no facts, only interpretations.", philosopher="Friedrich Nietzsche", context="avoidance", source="Notebooks"),
    Quote(text="What does not kill me makes me stronger.", philosopher="Friedrich Nietzsche", context="avoidance", source="Twilight of the Idols"),
    Quote(text="The snake which cannot cast its skin has to die.", philosopher="Friedrich Nietzsche", context="avoidance", source="Daybreak"),
    Quote(text="One must still have chaos in oneself to be able to give birth to a dancing star.", philosopher="Friedrich Nietzsche", context="avoidance", source="Thus Spoke Zarathustra"),
    Quote(text="In individuals, insanity is rare; but in groups, parties, nations and epochs, it is the rule.", philosopher="Friedrich Nietzsche", context="avoidance", source="Beyond Good and Evil"),
    Quote(text="Whoever fights monsters should see to it that in the process he does not become a monster.", philosopher="Friedrich Nietzsche", context="avoidance", source="Beyond Good and Evil"),
    Quote(text="The doer alone learns.", philosopher="Friedrich Nietzsche", context="avoidance", source="Thus Spoke Zarathustra"),
    Quote(text="Convictions are more dangerous foes of truth than lies.", philosopher="Friedrich Nietzsche", context="avoidance", source="Human, All Too Human"),

    # Seneca - overwhelm
    Quote(text="It is not that we have a short time to live, but that we waste a great deal of it.", philosopher="Seneca", context="overwhelm", source="On the Shortness of Life"),
    Quote(text="We suffer more in imagination than in reality.", philosopher="Seneca", context="overwhelm", source="Letters to Lucilius"),
    Quote(text="Difficulties strengthen the mind, as labor does the body.", philosopher="Seneca", context="overwhelm", source="Moral Letters"),
    Quote(text="Begin at once to live, and count each separate day as a separate life.", philosopher="Seneca", context="overwhelm", source="Moral Letters"),
    Quote(text="The whole future lies in uncertainty: live immediately.", philosopher="Seneca", context="overwhelm", source="Moral Letters"),
    Quote(text="A gem cannot be polished without friction, nor a man perfected without trials.", philosopher="Seneca", context="overwhelm", source="Moral Letters"),
    Quote(text="It is not because things are difficult that we do not dare, it is because we do not dare that things are difficult.", philosopher="Seneca", context="overwhelm", source="Moral Letters"),
    Quote(text="No man was ever wise by chance.", philosopher="Seneca", context="overwhelm", source="Moral Letters"),
    Quote(text="As is a tale, so is life: not how long it is, but how good it is, is what matters.", philosopher="Seneca", context="overwhelm", source="Moral Letters"),
    Quote(text="True happiness is to enjoy the present, without anxious dependence upon the future.", philosopher="Seneca", context="overwhelm", source="On the Happy Life"),

    # Sun Tzu - strategy
    Quote(text="Know thy enemy and know yourself; in a hundred battles, you will never be defeated.", philosopher="Sun Tzu", context="strategy", source="The Art of War"),
    Quote(text="In the midst of chaos, there is also opportunity.", philosopher="Sun Tzu", context="strategy", source="The Art of War"),
    Quote(text="Victorious warriors win first and then go to war, while defeated warriors go to war first and then seek to win.", philosopher="Sun Tzu", context="strategy", source="The Art of War"),
    Quote(text="The supreme art of war is to subdue the enemy without fighting.", philosopher="Sun Tzu", context="strategy", source="The Art of War"),
    Quote(text="Appear weak when you are strong, and strong when you are weak.", philosopher="Sun Tzu", context="strategy", source="The Art of War"),
    Quote(text="Let your plans be dark and impenetrable as night, and when you move, fall like a thunderbolt.", philosopher="Sun Tzu", context="strategy", source="The Art of War"),

    # Victory quotes
    Quote(text="Man is something that shall be overcome. What have you done to overcome him?", philosopher="Friedrich Nietzsche", context="victory", source="Thus Spoke Zarathustra"),
    Quote(text="The impediment to action advances action. What stands in the way becomes the way.", philosopher="Marcus Aurelius", context="victory", source="Meditations"),
    Quote(text="It is not the mountain we conquer, but ourselves.", philosopher="Edmund Hillary", context="victory", source="Attributed"),

    # Defeat / perseverance quotes
    Quote(text="Our greatest glory is not in never falling, but in rising every time we fall.", philosopher="Confucius", context="perseverance", source="Analects"),
    Quote(text="Fall seven times, stand up eight.", philosopher="Japanese Proverb", context="perseverance", source="Traditional"),
    Quote(text="The only way to do great work is to love what you do.", philosopher="Steve Jobs", context="perseverance", source="Stanford Commencement"),
    Quote(text="What we achieve inwardly will change outer reality.", philosopher="Plutarch", context="perseverance", source="Moralia"),
]
