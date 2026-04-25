package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"strings"
	"time"

	"github.com/gotd/td/telegram"
	"github.com/gotd/td/telegram/auth"
	"github.com/gotd/td/telegram/downloader"
	"github.com/gotd/td/tg"
	"golang.org/x/term"
)

type terminalAuth struct {
	phone string
}

func (terminalAuth) Phone(_ context.Context) (string, error) {
	return os.Getenv("PHONE_NUMBER"), nil
}

func (terminalAuth) Code(_ context.Context, _ *tg.AuthSentCode) (string, error) {
	fmt.Print("Enter code: ")
	code, err := term.ReadPassword(0)
	return string(code), err
}

func (terminalAuth) SignUp(_ context.Context) (auth.UserInfo, error) {
	return auth.UserInfo{}, nil
}

func (terminalAuth) AcceptTermsOfService(_ context.Context, tos tg.HelpTermsOfService) error {
	return nil
}

func main() {
	apiID := os.Getenv("API_ID")
	apiHash := os.Getenv("API_HASH")
	phone := os.Getenv("PHONE_NUMBER")
	usernames := strings.Split(os.Getenv("USERNAMES"), ",")

	if apiID == "" || apiHash == "" || phone == "" {
		fmt.Println("API_ID, API_HASH, PHONE_NUMBER required")
		return
	}

	sessionDir := "sessions"
	os.MkdirAll(sessionDir, 0755)

	client := telegram.NewClient(
		telegram.Config{
			AppID:    stringToInt(apiID),
			AppHash:  apiHash,
			SessionDir: sessionDir,
		},
		telegram.Options{},
	)

	flow := auth.NewFlow(
		terminalAuth{phone: phone},
		auth.SendCodeOptions{},
	)

	signals := make(chan os.Signal, 1)
	signal.Notify(signals, os.Interrupt)

	go func() {
		<-signals
		fmt.Println("\nStopping...")
		client.Stop()
	}()

	for {
		fmt.Printf("Checking %d usernames...\n", len(usernames))
		for _, username := range usernames {
			if username == "" {
				continue
			}
			_, err := client.Auth().Bot(context.Background(), func(ctx context.Context) error {
				return client.Run(ctx, func(ctx context.Context) error {
					api := tg.NewClient(client.API())
					_, err := api.ContactsResolveUsername(ctx, username)
					if err != nil {
						if strings.Contains(err.Error(), "USERNAME_NOT_OCCUPIED") {
							fmt.Printf("✅ Username @%s is FREE! Claiming...\n", username)
							// Claim username
							me, _ := api.UsersGetMe(ctx)
							_, err := api.AccountUpdateUsername(ctx, username)
							if err == nil {
								fmt.Printf("🏆 Successfully claimed @%s!\n", username)
								sendNotification(fmt.Sprintf("CLAIMED: @%s", username))
							} else {
								fmt.Printf("Failed to claim: %v\n", err)
							}
						}
					}
					return nil
				})
			})
			if err != nil {
				fmt.Printf("Error: %v\n", err)
			}
			time.Sleep(1 * time.Second)
		}
		time.Sleep(5 * time.Second)
	}
}

func stringToInt(s string) int {
	var i int
	fmt.Sscanf(s, "%d", &i)
	return i
}

func sendNotification(msg string) {
	webhook := os.Getenv("WEBHOOK_URL")
	if webhook != "" {
		// Send to Telegram webhook
	}
}
