import Hero from "./sections/Hero";
import RoleMap from "./sections/RoleMap";
import HiddenStructure from "./sections/HiddenStructure";
import LeadershipGap from "./sections/LeadershipGap";
import WordsVsWork from "./sections/WordsVsWork";
import Explorer from "./sections/Explorer";
import Methodology from "./sections/Methodology";
import "./sections/sections.css";

export default function App() {
  return (
    <main>
      <Hero />
      <RoleMap />
      <HiddenStructure />
      <LeadershipGap />
      <WordsVsWork />
      <Explorer />
      <Methodology />
    </main>
  );
}
