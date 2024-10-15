from bs4 import BeautifulSoup

def _getFirstSearchedElement(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        list_div = soup.find('div', id='hits')
        
        if not list_div:
            print("No se encontró el div con id 'hits'.")
            return None
        
        first_element = list_div.find('li')
        if not first_element:
            print("No se encontró ningún elemento 'li' dentro del div con id 'hits'.")
            return None
        
        link = first_element.find('a')
        if not link or 'href' not in link.attrs:
            print("No se encontró ningún enlace 'a' con el atributo 'href' dentro del primer elemento 'li'.")
            return None
        
        return link['href']
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Ejemplo de uso
html_content = '''<div id="hits" :class-names="{ 'ais-Hits': 'MyCustomHits', 'ais-Hits-list': 'MyCustomHitsList' }">
<div><div class="ais-Hits"><ol class="ais-Hits-list list-unstyled"><li class="ais-Hits-item">
<div class="media"><a class="pull-left" href="/series/jobless-reincarnation-it-will-be-all-out-if-i-go-to-another-world">
<img class="media-object img-rounded" src="https://artworks.thetvdb.com/banners/v4/series/371310/posters/64903a85960eb.jpg"></a>
<div class="media-body"><h3 class="media-heading">
<a href="/series/jobless-reincarnation-it-will-be-all-out-if-i-go-to-another-world">Mushoku Tensei: Jobless Reincarnation</a></h3> 
<div class="text-muted">2021, Series #371310</div><div class="vt-content"><p>Killed while saving a stranger from a traffic collision, a 34-year-old NEET is reincarnated into a world of magic as Rudeus Greyrat, a newborn baby. With knowledge, experience, and regrets from his previous life retained, Rudeus vows to lead a fulfilling life and not repeat his past mistakes.

Now gifted with a tremendous amount of magical power and the mind of a grown adult, Rudeus is seen as a genius in the making by his new parents. Soon, he finds himself studying under powerful warriors, such as his swordsman father and a mage named Roxy Migurdia—all in order to hone his apparent talents. But despite his innocent exterior, Rudeus is still a perverted otaku, who uses his wealth of knowledge to make moves on women who would have been out of reach in his past life.</p><h5 class="mb-0 mt-2">Alternate Titles:</h5><ul class="list-inline"><li>無職転生 ～異世界行ったら本気だす～</li><li>Mushoku Tensei: Jobless Reincarnation</li><li>무직전생 ~이세계에 갔으면 최선을 다한다~</li><li>Mushoku Tensei: Przegryw w innym świecie</li><li>Реинкарнация безработного</li><li>Mushoku Tensei: Reencarnación desde cero</li><li>Реінкарнація безробітного: В інший світ на повному серйозі</li><li>无职转生～到了异世界就拿出真本事～</li><li>無職轉生，到了異世界就拿出真本事</li><li>Mushoku Tensei</li><li>Jobless Reincarnation</li><li>Jobless Reincarnation: I Will Seriously Try If I Go to Another World</li><li>Jobless Reincarnation: I Will Seriously Try If I Go To Another World</li><li>Mushoku Tensei: Isekai Ittara Honki Dasu</li><li>Mushoku Tensei II: Isekai Ittara Honki Dasu</li><li>Mushoku Tensei II: Isekai Ittara Honki Dasu Part 2</li><li>Mushoku Tensei II - Isekai Ittara Honki Dasu Part 2</li><li>Reencarnação sem uma Função: Se Estou num Outro Mundo, Irei com Tudo</li><li>Реинкарнация безработного: История о приключениях в другом мире</li><li>无职转生</li><li>Реінкарнація безробітного: в іншому світі я не облажаюся</li><li>Reinkarnatsiya bezrobitnogo 2</li><li>reinkarnatsiya bezrobitnogo</li></ul></div></div></div></li><li class="ais-Hits-item"><div class="media">
<a class="pull-left" href="/series/mushoku-no-eiyuu"><img class="media-object img-rounded" src="https://artworks.thetvdb.com/banners/images/missing/series.jpg"></a>
<div class="media-body"><h3 class="media-heading"><a href="/series/mushoku-no-eiyuu">The Hero Who Has No Class</a></h3> <div class="text-muted">Series #440502</div><div class="vt-content"><p>“Classes” are given at the age of 10, and the presence or absence of “skills” greatly affect life. Arel, the son of “Sword Princess” Fara and “Magic King” Leon, has been branded as “Classless”… But even without a job or skills, Arel believes he can persevere through effort.</p><h5 class="mb-0 mt-2">Alternate Titles:</h5><ul class="list-inline"><li>無職の英雄 別にスキルなんか要らなかったんだが</li><li>The Hero Who Has No Class</li><li>Mushoku no Eiyuu : Betsu ni Skill Nanka Iranakattan da ga</li><li>Mushoku no Eiyū: Betsu ni Skill Nanka Iranakattan da ga</li><li>Mushoku no Eiyuu: Betsu ni Skill Nanka Iranakattan da ga</li><li>The Classless Hero: I Didn't Need Skills Anyway</li><li>The Hero Who Has No Class. I Don't Need Any Skills, It's Okay.</li><li>The Unemployed Hero Does Not Need Something Like Skills</li></ul></div></div></div></li><li class="ais-Hits-item"><div class="media"><a class="pull-left" href="/movies/slaughter-in-the-snow"><img class="media-object img-rounded" src="https://artworks.thetvdb.com/banners/movies/190973/posters/e7vXwnPjobgJnxLqYw4IFsSTQps.jpg"></a>
<div class="media-body"><h3 class="media-heading"><a href="/movies/slaughter-in-the-snow">Slaughter in the Snow</a></h3> <div class="text-muted">1973, Movie #190973</div><div class="vt-content"><p>In feudal Japan, women are vulnerable, in need of protection, and capable of deception. Jokichi of Mikogami, a drifter, has not yet fully revenged the death of his wife and son. He searches for Kunisada Chuji, who in turn has hired the knife-throwing Windmill Kobunji to kill him. Kobunji and Jokichi meet in the winter, near Sasago Pass, when both have rescued women: Jokichi has saved the lute-playing Oyae whose clan and whose lover want her dead; Kobunji has rescued Oharu, a well-born woman married to an innkeeper. Is this rescue a whim or something deeper? And why does Jokichi become the consumptive Kobunji's protector? What ultimately will Jokichi do about Oyae?</p><h5 class="mb-0 mt-2">Alternate Titles:</h5><ul class="list-inline"><li>Mushukunin mikogami no jôkichi: Tasogare ni senko ga tonda</li><li>Slaughter in the Snow</li><li>Резня в снегу</li></ul></div></div></div></li></ol></div></div></div>'''

print(_getFirstSearchedElement(html_content))
