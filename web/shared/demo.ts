import type { Language, Philosopher } from "./prompts.js";

type Localized = Record<Language, string>;
export type DemoTopic = "assumptions" | "evidence" | "perspectives" | "uncertainty" | "followup" | "human";
type DemoQuestion = {
  label: Localized;
  replies: Record<Philosopher, Localized>;
  next: DemoTopic[];
};

// Curated reflection themes, not clinical conclusions or an executable research protocol.
export const demoQuestions: Record<DemoTopic, DemoQuestion> = {
  assumptions: {
    label: { nl: "Mijn eerste indruk stuurt mijn verdere redenering.", en: "My first impression is steering my subsequent reasoning." },
    replies: {
      socrates: { nl: "Wat bedoel je precies met je eerste indruk: welke waarneming en welke interpretatie onderscheid je daarin?", en: "What exactly do you mean by your first impression: which observation and which interpretation do you distinguish within it?" },
      nietzsche: { nl: "Een eerste indruk kan een werkhypothese zijn, geen vaststaand feit. Welke aanname zou je opnieuw onderzoeken als je die indruk even losliet?", en: "A first impression can be a working hypothesis, not an established fact. Which assumption would you revisit if you set that impression aside?" },
      zarathustra: { nl: "Onzekerheid toelaten is ruimte maken voor reflectie. Welk ander perspectief zou jouw eerste indruk kunnen aanvullen?", en: "Allowing uncertainty makes room for reflection. What other perspective might complement your first impression?" },
    },
    next: ["evidence", "uncertainty", "perspectives"],
  },
  evidence: {
    label: { nl: "Ik wil mijn werkhypothese op tegenbewijs toetsen.", en: "I want to examine evidence against my working hypothesis." },
    replies: {
      socrates: { nl: "Welke concrete waarneming in deze fictieve casus zou het sterkst tegen jouw werkhypothese spreken?", en: "Which concrete observation in this fictional case would most strongly challenge your working hypothesis?" },
      nietzsche: { nl: "Onderbouwing is niet hetzelfde als bevestiging zoeken. Welke bevinding zou je overtuiging kunnen veranderen, ook als die niet bij je eerste verklaring past?", en: "Supporting a hypothesis is not the same as seeking confirmation. Which finding could change your belief even if it does not fit your first explanation?" },
      zarathustra: { nl: "Een hypothese kunnen herzien is een vorm van verantwoordelijkheid. Wat zou jou helpen om tegenbewijs evenveel ruimte te geven als bevestiging?", en: "Being able to revise a hypothesis is a form of responsibility. What would help you give counterevidence as much space as confirmation?" },
    },
    next: ["uncertainty", "followup", "human"],
  },
  perspectives: {
    label: { nl: "Neurologie, psychiatrie en neuropsychologie kijken met andere brillen.", en: "Neurology, psychiatry, and neuropsychology bring different perspectives." },
    replies: {
      socrates: { nl: "Welke betekenis geven de verschillende disciplines aan dezelfde waarneming in deze fictieve casus?", en: "What meaning do the different disciplines give to the same observation in this fictional case?" },
      nietzsche: { nl: "De vertrouwde bril is niet de enige bril. Welke veronderstelling binnen jouw discipline zou een collega uit een andere discipline bevragen?", en: "The familiar lens is not the only lens. Which assumption in your discipline might a colleague from another discipline question?" },
      zarathustra: { nl: "Verschillende perspectieven hoeven elkaar niet uit te sluiten. Hoe zou je ruimte maken voor de stem van de patiënt naast de professionele verklaringsmodellen?", en: "Different perspectives need not exclude one another. How would you make room for the patient's voice alongside professional explanatory models?" },
    },
    next: ["assumptions", "uncertainty", "followup"],
  },
  uncertainty: {
    label: { nl: "Ik wil onderscheid maken tussen observatie, interpretatie en onzekerheid.", en: "I want to distinguish observation, interpretation, and uncertainty." },
    replies: {
      socrates: { nl: "Welk deel van jouw redenering is een waarneming en welk deel is een nog te toetsen interpretatie?", en: "Which part of your reasoning is an observation and which part is an interpretation still to be examined?" },
      nietzsche: { nl: "Zeker klinken is niet hetzelfde als zeker weten. Waar in je redenering gebruik je een stellig woord terwijl de onderbouwing nog onzeker is?", en: "Sounding certain is not the same as knowing for certain. Where in your reasoning are you using a definite word while the evidence remains uncertain?" },
      zarathustra: { nl: "Je hoeft onzekerheid niet weg te drukken om zorgvuldig te reflecteren. Hoe zou je de grenzen van je huidige kennis expliciet verwoorden?", en: "You do not have to suppress uncertainty to reflect carefully. How would you explicitly describe the limits of your current knowledge?" },
    },
    next: ["evidence", "followup", "human"],
  },
  followup: {
    label: { nl: "We willen redeneringen over meerdere jaren en centra volgen.", en: "We want to follow reasoning across multiple years and centres." },
    replies: {
      socrates: { nl: "Wat zou je door de tijd willen onderscheiden: een verandering in de patiënt, in de beschikbare informatie of in jouw interpretatie?", en: "What would you want to distinguish over time: a change in the patient, in available information, or in your interpretation?" },
      nietzsche: { nl: "Een latere uitkomst bewijst niet vanzelf dat de eerdere redenering goed was. Welke vooraf vastgelegde criteria zouden helpen om het redeneerproces eerlijk te beoordelen?", en: "A later outcome does not automatically prove the earlier reasoning was sound. Which predefined criteria would help assess the reasoning process fairly?" },
      zarathustra: { nl: "Meer kritische vragen betekenen nog niet bewezen betere zorg. Hoe zou je onderzoeken of een verandering in het redeneerproces ook zonder de tool standhoudt?", en: "More critical questions do not yet demonstrate better care. How would you examine whether a change in reasoning persists without the tool?" },
    },
    next: ["human", "perspectives", "evidence"],
  },
  human: {
    label: { nl: "De professional moet verantwoordelijk blijven, niet de AI.", en: "The professional must remain responsible, not the AI." },
    replies: {
      socrates: { nl: "Wat betekent menselijke verantwoordelijkheid concreet wanneer een systeem je redenering bevraagt?", en: "What does human responsibility mean concretely when a system questions your reasoning?" },
      nietzsche: { nl: "Ook een overtuigend geformuleerde AI-vraag kan een nieuwe bias introduceren. Hoe zou je merken dat je de vraag van het systeem te veel autoriteit geeft?", en: "Even a persuasively worded AI question can introduce a new bias. How would you notice that you are giving the system's question too much authority?" },
      zarathustra: { nl: "De tool is een sparringpartner, geen diagnostische autoriteit. Welke grens wil je expliciet bewaken tussen reflectieondersteuning en een zorgbeslissing?", en: "The tool is a sparring partner, not a diagnostic authority. What boundary do you want to maintain explicitly between reflection support and a care decision?" },
    },
    next: ["assumptions", "perspectives", "followup"],
  },
};

export const initialDemoTopics: DemoTopic[] = ["assumptions", "perspectives", "human"];

export const customDemoReply: Localized = {
  nl: "Dit is een gescripte demonstratie: er is geen echte LLM-integratie actief. Vrije tekst wordt niet inhoudelijk geanalyseerd of verstuurd. Kies een van de voorgestelde onderwerpen om de voorbeeldvragen te verkennen.",
  en: "This is a scripted demonstration: no actual LLM integration is running. Free text is not analysed or sent anywhere. Choose one of the suggested topics to explore the example questions.",
};

export function demoReply(topic: DemoTopic | undefined, language: Language, philosopher: Philosopher): string {
  return topic ? demoQuestions[topic].replies[philosopher][language] : customDemoReply[language];
}
