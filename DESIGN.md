# Portfolio design and content

The current design restores the original green landing-page structure: a large **My portfolio** heading, the existing practical project introduction, an animated orbital scene, the six project cards, and a **Contact me** section. The previous slogans, ticker, decorative text labels, and promotional copy remain removed. The contact section uses existing configured links; with no email configured, GitHub is available.

All visible site logos and the owner's real name have been removed from the public page, its title and social metadata, and the public-content snapshot. The private admin header also has no logo. The only site icon is a plain white **R** on a black square, used as the browser favicon rather than a page logo. Supplied project screenshots remain project content.

The theme returns to the original dark green-gray background and lime-green accent (`#d1fd78`). The hero's orbital artwork uses CSS and respects reduced-motion preferences; animation pauses when the tab is hidden. Project details still open in keyboard-dismissible dialogs, where supplied screenshots can be viewed in full.

[projects.md](projects.md) is the supplied source for all six projects. Descriptions have been lightly edited for spelling and readability without adding features, dates, completion claims, or project links. Only acq and My own environment are marked In development because the source explicitly says they are current work. Project years remain editable data but are not displayed because the source did not supply dates.

| Project | Supplied image | Public asset |
| --- | --- | --- |
| Self-sustaining plant box | `taimed.jpg` | `static/projects/plant-box.jpg` |
| Fastbite | `fastbite.png` | `static/projects/fastbite.png` |
| Gmail summaries | `Pasted image (2).png` (the n8n screenshot) | `static/projects/gmail-summaries.png` |
| Agent farm | `Pasted image.png` | `static/projects/agent-farm.png` |
| acq | None supplied | Text-only card |
| My own environment | None supplied | Text-only card |

Images are the owner's supplied originals, self-hosted with descriptive filenames. Project screenshots retain their colors. The photo is cropped only by the card's CSS presentation; the original remains available in its detail dialog. No generated replacement images were used.

Space Grotesk is self-hosted at `static/fonts/space-grotesk.ttf`, with the SIL Open Font License in `static/fonts/OFL.txt`. No external font requests, analytics, or third-party JavaScript execute in visitors' browsers. The earlier design used [Codrops' 3D portfolio work](https://tympanus.net/codrops/2025/01/21/the-journey-of-creating-a-3d-portfolio/) as inspiration; the current landing-page layout restores its orbital visual direction with minimal copy.
