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

	// Integer conversion
	var appID int
	fmt.Sscanf(apiID, "%d", &appID)

	client := telegram.NewClient(
		appID,
		apiHash,
		telegram.Options{
			SessionStorage: &telegram.FileSessionStorage{
				Path: sessionDir,
			},
		},
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

	fmt.Println("Starting username sniper...")
	
	err := client.Run(context.Background(), func(ctx context.Context) error {
		api := tg.NewClient(client.API())
		
		// Login
		if err := client.Auth().IfNecessary(ctx, flow); err != nil {
			return fmt.Errorf("auth failed: %w", err)
		}
		
		me, err := api.UsersGetMe(ctx)
		if err != nil {
			return fmt.Errorf("get me failed: %w", err)
		}
		fmt.Printf("Logged in as: %s\n", me.Username)
		
		for {
			fmt.Printf("Checking %d usernames...\n", len(usernames))
			for _, username := range usernames {
				username = strings.TrimSpace(username)
				if username == "" {
					continue
				}
				
				// Check if username is available
				_, err := api.ContactsResolveUsername(ctx, username)
				if err != nil {
					if strings.Contains(err.Error(), "USERNAME_NOT_OCCUPIED") {
						fmt.Printf("✅ Username @%s is FREE! Claiming...\n", username)
						_, err := api.AccountUpdateUsername(ctx, username)
						if err == nil {
							fmt.Printf("🏆 Successfully claimed @%s!\n", username)
						} else {
							fmt.Printf("Failed to claim: %v\n", err)
						}
					}
				}
				time.Sleep(2 * time.Second)
			}
			time.Sleep(10 * time.Second)
		}
	})
	
	if err != nil {
		fmt.Printf("Error: %v\n", err)
	}
}
