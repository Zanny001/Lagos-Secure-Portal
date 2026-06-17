# IGCSE Extended Physics: Core Instructional Notes
## Topic: Nuclear Physics (Fission, Fusion, and Decay Mechanics)

---

### 1. The Structure of the Atom & Mass Defect Theory
Every atom consists of a positively charged nucleus containing protons and neutrons (collectively called nucleons), surrounded by negatively charged electrons. 

* **Proton Number ($Z$):** The number of protons in the nucleus (defines the element).
* **Nucleon Number ($A$):** The total number of protons and neutrons combined.

#### The Mass Defect ($\Delta m$)
Crucially, the measured mass of a fully bound atomic nucleus is always slightly **less** than the sum of the individual masses of its constituent protons and neutrons when completely separated. This missing mass is known as the **mass defect**.
$$\Delta m = (Z \cdot m_p + (A - Z) \cdot m_n) - m_{nucleus}$$

This mass loss isn't destroyed; it is converted directly into energy during nuclear formation—known as the **Binding Energy** ($E$) holding the nucleus together—governed by Einstein's mass-energy equivalence equation:
$$E = \Delta m \cdot c^2$$
*Where:*
* $E$ = Energy released (Joules, $\text{J}$)
* $\Delta m$ = Mass defect (Kilograms, $\text{kg}$)
* $c$ = Speed of light ($3.0 \times 10^8 \text{ m/s}$)

---

### 2. Nuclear Fission vs. Nuclear Fusion



#### A. Nuclear Fission
* **Definition:** The splitting of a heavy, unstable nucleus (such as Uranium-235 or Plutonium-239) into two lighter, more stable daughter nuclei, accompanied by the release of neutrons and a massive quantity of kinetic energy.
* **Mechanism:** A slow-moving neutron is captured by a $\text{U-235}$ nucleus, forcing it into an highly unstable state ($\text{U-236}$). It splits rapidly, releasing energy along with 2 or 3 secondary fast neutrons.
* **Chain Reactions:** If these emitted neutrons are slowed down (by a moderator) and captured by adjacent fissile nuclei, a self-sustaining *controlled chain reaction* is established (the core principle of commercial nuclear power reactors). Uncontrolled chain reactions result in nuclear weapons.

$$\text{n}_0^1 + \text{U}_{92}^{235} \rightarrow \text{Ba}_{56}^{141} + \text{Kr}_{36}^{92} + 3\text{n}_0^1 + \text{Energy}$$

#### B. Nuclear Fusion
* **Definition:** The combining of two light, low-mass nuclei (such as isotopes of Hydrogen: Deuterium $\text{H}_1^2$ and Tritium $\text{H}_1^3$) at extremely high velocities to form a heavier, more stable nucleus (Helium-4) with the release of enormous amounts of energy.
* **Conditions Required:** Fusion requires extraordinarily high temperatures (approx. $15 \times 10^6 \text{ }^\circ\text{C}$) and massive pressure, such as those found in the core of active stars (like our Sun). High temperature gives the nuclei sufficient kinetic energy to overcome the immense electrostatic repulsive force (Coulomb barrier) between the positively charged protons.

$$\text{H}_1^2 + \text{H}_1^3 \rightarrow \text{He}_2^4 + \text{n}_0^1 + \text{Energy}$$

#### Summary Comparison for Examinations:
| Metric | Nuclear Fission | Nuclear Fusion |
| :--- | :--- | :--- |
| **Reactants** | Heavy, massive nuclei ($\text{U-235}$) | Light, low-mass nuclei ($\text{H}-2, \text{H}-3$) |
| **Products** | Lighter daughter nuclei + free neutrons | Heavier, stable nucleus ($\text{He}-4$) + free neutrons |
| **Energy Yield** | High per reaction event | Extremely High (approx. 4x higher per unit mass than fission) |
| **Conditions** | Requires neutron bombardment entry | Requires ultra-high temperatures & pressures |

---

### 3. Radioactive Decay Mechanics & Half-Life Kinetics
Radioactive decay is a completely **random** and **spontaneous** process by which unstable atomic nuclei lose energy by emitting ionizing radiation.

* **Random:** It is impossible to predict exactly which individual nucleus will decay next; however, a large statistical sample follows a clear mathematical decay pattern.
* **Spontaneous:** The rate of decay is completely unaffected by external physical conditions such as temperature, pressure, or chemical bonding configurations.

#### Types of Ionizing Radiation:
1. **Alpha ($\alpha$):** Helium nucleus ($\text{He}_2^4$). High ionizing power, low penetrating power (stopped by paper/skin).
2. **Beta ($\beta^-$):** High-energy electron ($\text{e}_{-1}^0$). Moderate ionizing power, moderate penetrating power (stopped by a few millimeters of aluminum).
3. **Gamma ($\gamma$):** High-frequency electromagnetic wave ($\gamma_0^0$). Low ionizing power, extremely high penetrating power (attenuated only by thick lead or dense concrete blocks).

#### Half-Life ($T_{1/2}$)
The half-life of a radioactive isotope is the time taken for half of the unstable nuclei originally present in a sample to decay, or the time taken for the initial activity (measured in Becquerels, $\text{Bq}$) to drop to half of its original value.

---

### 4. Step-by-Step Mathematical Worked Examples

#### Example 1: Mass-Energy Equivalence
A specific nuclear fission reaction results in a calculated mass defect ($\Delta m$) of $3.2 \times 10^{-28} \text{ kg}$. Calculate the total binding energy released during this single reaction event.

**Solution:**
1. State the required formula:
   $$E = \Delta m \cdot c^2$$
2. Identify the constants and given variables:
   * $\Delta m = 3.2 \times 10^{-28} \text{ kg}$
   * $c = 3.0 \times 10^8 \text{ m/s}$
3. Substitute values into the equation framework:
   $$E = (3.2 \times 10^{-28}) \times (3.0 \times 10^8)^2$$
   $$E = (3.2 \times 10^{-28}) \times (9.0 \times 10^{16})$$
4. Compute the final numeric evaluation:
   $$E = 2.88 \times 10^{-11} \text{ Joules}$$

#### Example 2: Half-Life Decay Calculation
A radioactive sample discovered in a laboratory tracking node has an initial activity count rate of $1200 \text{ counts/minute}$. The isotope has a known half-life ($T_{1/2}$) of $4 \text{ hours}$. Calculate the activity remaining after exactly $16 \text{ hours}$ have elapsed.

**Solution:**
1. Determine the total number of half-life cycles ($n$) that fit within the elapsed duration:
   $$n = \frac{\text{Total Time Elapsed}}{\text{Half-Life Duration}} = \frac{16 \text{ hours}}{4 \text{ hours}} = 4 \text{ cycles}$$
2. Apply the fractional reduction formula step-by-step:
   $$\text{Final Activity} = \text{Initial Activity} \times \left(\frac{1}{2}\right)^n$$
   $$\text{Final Activity} = 1200 \times \left(\frac{1}{2}\right)^4$$
   $$\text{Final Activity} = 1200 \times \frac{1}{16}$$
3. Final numeric output division:
   $$\text{Final Activity} = 75 \text{ counts/minute}$$
