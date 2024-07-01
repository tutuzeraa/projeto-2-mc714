# Instruções para execução

1. Editar ```gera_docker.py``` para definir a quantidade de nós desejada e especificar os nós para eleição inicial. Executar o script para criar/atualizar ```docker-compose.yml```.
2. Abrir terminal neste diretório (leader_election)
3. Para executar o algoritmo, executar

    ```
    sudo docker compose build && sudo docker compose up -d && sudo docker compose logs -f
    ```
4. Para interromper a execução: comando CTRL+C
5. Para parar e remover os container, execute
    ```
    sudo docker compose down
    ```
```


