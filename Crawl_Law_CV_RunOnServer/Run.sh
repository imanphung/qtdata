rm -r CV_Crawl.csv
scp /Users/phungan/Documents/QTData/Database\ 2/linkedin_data.csv qtdatavn@118.69.32.128:/home/qtdatavn/data2020/linkedin_data
sleep 5
ssh -t qtdatavn@42.117.134.234 <<EOF
cd /home/qtdatavn/crawl_law_data
scrapy crawl getinfo
EOF
scp qtdatavn@118.69.32.128:/home/qtdatavn/data2020/linkedin_data/linkedin_data.csv /Users/phungan/Documents/QTData/Database\ 2
sleep 5